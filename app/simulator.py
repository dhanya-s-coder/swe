from dataclasses import dataclass
import heapq
import numpy as np

@dataclass
class Machine:
    machine_id: str; category: str; mttf: float; repair_min: float; repair_max: float
    status: str = 'RUNNING'; running_since: float = 0.0; running_time: float = 0.0; failures: int = 0

@dataclass
class Adjuster:
    adjuster_id: str; skills: set; skill_capacity: dict; status: str = 'IDLE'; busy_time: float = 0.0

def run_simulation(scenario):
    rng=np.random.default_rng(scenario.seed); machines=[]; adjusters=[]; events=[]; seq=0; waiting=[]; repairs={}
    for cfg in scenario.machine_configs:
        for i in range(cfg.count): machines.append(Machine(f'{cfg.category.upper()}-{i+1:04d}',cfg.category,cfg.mttf,cfg.repair_min,cfg.repair_max))
    for a in scenario.adjusters: adjusters.append(Adjuster(a.adjuster_id,set(a.skills),dict(a.skill_capacity)))
    by_id={m.machine_id:m for m in machines}
    def failure_time(mean):
        # Gaussian pseudo-random failure interval, clipped so time is positive.
        return float(max(0.1, rng.normal(mean, max(0.1, mean * 0.10))))
    for m in machines:
        seq+=1; heapq.heappush(events,(failure_time(m.mttf),seq,'FAILURE',m.machine_id))
    def assign(now):
        nonlocal seq
        while True:
            pair=None
            for idx,mid in enumerate(waiting):
                compatible=[a for a in adjusters if a.status=='IDLE' and by_id[mid].category in a.skills]
                if compatible:
                    pair=(idx,mid,min(compatible,key=lambda x:(len(x.skills),x.adjuster_id))); break
            if pair is None: return
            idx,mid,a=pair; waiting.pop(idx); m=by_id[mid]; m.status='REPAIR'; a.status='BUSY'; duration=float(rng.uniform(m.repair_min,m.repair_max)); repairs[mid]=(a.adjuster_id,now,duration); seq+=1; heapq.heappush(events,(now+duration,seq,'REPAIR_DONE',mid))
    while events:
        now,_,kind,mid=heapq.heappop(events)
        if now>scenario.duration: break
        m=by_id[mid]
        if kind=='FAILURE' and m.status=='RUNNING':
            m.running_time+=max(0,now-m.running_since); m.status='FAILED'; m.failures+=1
            candidates=[x for x in adjusters if x.status=='IDLE' and m.category in x.skills]
            a=min(candidates,key=lambda x:(len(x.skills),x.adjuster_id)) if candidates else None
            if a:
                a.status='BUSY'; m.status='REPAIR'; duration=float(rng.uniform(m.repair_min,m.repair_max)); repairs[mid]=(a.adjuster_id,now,duration); seq+=1; heapq.heappush(events,(now+duration,seq,'REPAIR_DONE',mid))
            else: m.status='WAITING'; waiting.append(mid)
        elif kind=='REPAIR_DONE' and m.status=='REPAIR':
            aid,started,duration=repairs.pop(mid); a=next(x for x in adjusters if x.adjuster_id==aid); end=min(now,scenario.duration); a.busy_time+=max(0.0,end-max(started,scenario.warmup)); a.status='IDLE'; m.status='RUNNING'; m.running_since=now; seq+=1; heapq.heappush(events,(now+failure_time(m.mttf),seq,'FAILURE',mid)); assign(now)
    obs=max(1e-9,scenario.duration-scenario.warmup); n=max(1,len(machines));
    categories={}
    for category in sorted({m.category for m in machines}):
        group=[m for m in machines if m.category==category]
        categories[category]={'machine_count':len(group),'failures':sum(m.failures for m in group),'machine_utilization':float(min(1.0,sum(max(0,m.running_time-scenario.warmup) for m in group)/(max(1,len(group))*obs)))}
    details=[{'machine_id':m.machine_id,'category':m.category,'status':m.status,'failures':m.failures,'running_seconds':round(max(0,m.running_time-scenario.warmup),2),'efficiency_percent':round(min(1.0,max(0,m.running_time-scenario.warmup)/obs)*100,2)} for m in machines]
    return {'machine_utilization':float(min(1.0,sum(max(0,m.running_time-scenario.warmup) for m in machines)/(n*obs))),'adjuster_utilization':float(min(1.0,sum(a.busy_time for a in adjusters)/(max(1,len(adjusters))*obs))),'machine_count':len(machines),'adjuster_count':len(adjusters),'failures':sum(m.failures for m in machines),'waiting_machines':sum(m.status=='WAITING' for m in machines),'queue_length':len(waiting),'downtime':float(sum(max(0,obs-(max(0,m.running_time-scenario.warmup))) for m in machines)),'categories':categories,'machines':details}

def run_replications(scenario, replications=10):
    results=[run_simulation(type(scenario)(scenario.machine_configs,scenario.adjusters,scenario.duration,scenario.warmup,scenario.seed+i)) for i in range(replications)]
    import numpy as np
    def summary(key):
        values=np.array([r[key] for r in results],dtype=float); mean=float(values.mean()); margin=float(1.96*values.std(ddof=1)/max(1,np.sqrt(len(values)))) if len(values)>1 else 0.0
        return {'mean':mean,'ci95_low':mean-margin,'ci95_high':mean+margin}
    return {'replications':replications,'machine_utilization':summary('machine_utilization'),'adjuster_utilization':summary('adjuster_utilization'),'avg_waiting_machines':summary('waiting_machines'),'failures':summary('failures')}
