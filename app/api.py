from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from .models import MachineConfig, AdjusterConfig, Scenario
from .simulator import run_simulation, run_replications
from .db import save_run
app=FastAPI(title='Factory Adjuster Simulation API')
class MachineIn(BaseModel):
    category:str; count:int=Field(gt=0); mttf:float=Field(gt=0); repair_time:float=Field(gt=0)
    @property
    def repair_min(self): return self.repair_time
    @property
    def repair_max(self): return self.repair_time
class AdjusterIn(BaseModel): adjuster_id:str; skills:List[str]; skill_capacity:dict[str,int]={}
class RunIn(BaseModel):
    machines:List[MachineIn]; adjusters:List[AdjusterIn]; duration:float=Field(default=300,ge=30); warmup:float=Field(default=0,ge=0); seed:int=1; save:bool=True
class ExperimentIn(RunIn):
    adjuster_counts:List[int]=[1,2,3,4,5]; mttf_multipliers:List[float]=[0.8,1.0,1.2]; machine_multipliers:List[float]=[0.5,1.0,2.0]; replications:int=10
@app.get('/health')
def health(): return {'status':'ok'}
@app.post('/simulate')
def simulate(payload:RunIn):
    if payload.warmup >= payload.duration: raise HTTPException(400,'warmup must be smaller than duration')
    if not payload.adjusters: raise HTTPException(400,'at least one adjuster is required')
    if any(not x.skills for x in payload.adjusters): raise HTTPException(400,'each adjuster needs at least one skill')
    scenario=Scenario([MachineConfig(x.category,x.count,x.mttf,x.repair_time,x.repair_time) for x in payload.machines],[AdjusterConfig(**x.model_dump()) for x in payload.adjusters],payload.duration,payload.warmup,payload.seed)
    result=run_simulation(scenario)
    if payload.save:
        try: save_run(result,payload.model_dump())
        except Exception as e: result['database_warning']=str(e)
    return result
@app.post('/experiment')
def experiment(payload:ExperimentIn):
    if payload.warmup >= payload.duration: raise HTTPException(400,'warmup must be smaller than duration')
    rows=[]
    for mm in payload.machine_multipliers:
      for fm in payload.mttf_multipliers:
       for count in payload.adjuster_counts:
        machines=[MachineConfig(x.category,max(1,round(x.count*mm)),x.mttf*fm,x.repair_time,x.repair_time) for x in payload.machines]
        skill_union=sorted({s for a in payload.adjusters for s in a.skills})
        capacity={s:min([a.skill_capacity.get(s,1) for a in payload.adjusters if s in a.skills] or [1]) for s in skill_union}
        adjusters=[AdjusterConfig(f'A-{i+1:03d}',skill_union,capacity) for i in range(count)]
        s=Scenario(machines,adjusters,payload.duration,payload.warmup,payload.seed+count)
        r=run_replications(s,payload.replications); rows.append({'machine_multiplier':mm,'mttf_multiplier':fm,'adjuster_count':count,'machine_utilization':r['machine_utilization']['mean'],'adjuster_utilization':r['adjuster_utilization']['mean'],'ci95_machine_low':r['machine_utilization']['ci95_low'],'ci95_machine_high':r['machine_utilization']['ci95_high'],'avg_waiting_machines':r['avg_waiting_machines']['mean']})
    eligible=[r for r in rows if r['machine_utilization']>=0.90 and r['avg_waiting_machines']<=1]
    optimum=min(eligible,key=lambda r:r['adjuster_count']) if eligible else max(rows,key=lambda r:r['machine_utilization'])
    return {'rows':rows,'optimum':optimum}
