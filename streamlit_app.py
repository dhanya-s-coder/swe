import os, requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title='Factory Simulator', layout='wide')
st.title('Factory Machine and Adjuster Simulator')
api=os.getenv('API_URL','http://localhost:8000')
skills=['lathe','turning','drilling','soldering','milling']
if 'machines_cfg' not in st.session_state: st.session_state.machines_cfg=[]
if 'adjusters_cfg' not in st.session_state: st.session_state.adjusters_cfg=[]

def next_adjuster_id():
    highest=0
    for item in st.session_state.adjusters_cfg:
        try: highest=max(highest,int(item['adjuster_id'].split('-')[-1]))
        except (ValueError, IndexError): pass
    return f'A-{highest+1:03d}'

st.sidebar.header('Simulation')
duration=st.sidebar.number_input('Simulated timeline (seconds)',30,1000000,300)
seed=st.sidebar.number_input('Random seed',1,999999,42)
st.sidebar.caption('This is virtual factory time, not waiting time. The simulation runs computationally and should finish within 1-2 minutes.')

left,right=st.columns(2)
with left:
    st.subheader('Machines')
    with st.form('add_machine', clear_on_submit=True):
        category=st.selectbox('Machine category',skills)
        count=st.number_input('How many machines to add',1,10000,1)
        mttf=st.number_input('Mean time to failure (seconds)',1.0,100000.0,20.0)
        repair=st.number_input('Repair time (seconds)',0.1,100000.0,5.0)
        if st.form_submit_button('Add machines'):
            st.session_state.machines_cfg.append({'category':category,'count':int(count),'mttf':float(mttf),'repair_time':float(repair)})
    if st.session_state.machines_cfg:
        st.dataframe(pd.DataFrame(st.session_state.machines_cfg), use_container_width=True, hide_index=True)
        machine_remove=st.selectbox('Select machine group to remove',range(len(st.session_state.machines_cfg)),format_func=lambda i: f"{st.session_state.machines_cfg[i]['category']} ({st.session_state.machines_cfg[i]['count']} machines)",key='machine_remove')
        if st.button('Remove selected machine group'):
            st.session_state.machines_cfg.pop(machine_remove); st.rerun()
with right:
    st.subheader('Adjusters')
    with st.form('add_adjuster', clear_on_submit=True):
        aid=st.text_input('Adjuster ID',next_adjuster_id())
        selected=st.multiselect('Skills',skills,default=[skills[0]])
        if st.form_submit_button('Add adjuster'):
            existing={a['adjuster_id'] for a in st.session_state.adjusters_cfg}
            if aid in existing: st.error('Adjuster ID already exists. Choose a unique ID.')
            elif selected: st.session_state.adjusters_cfg.append({'adjuster_id':aid,'skills':selected,'skill_capacity':{x:1 for x in selected}})
    if st.session_state.adjusters_cfg:
        st.dataframe(pd.DataFrame([{'adjuster_id':a['adjuster_id'],'skills':', '.join(a['skills']),'skill_count':len(a['skills'])} for a in st.session_state.adjusters_cfg]),use_container_width=True,hide_index=True)
        adjuster_remove=st.selectbox('Select adjuster to remove',range(len(st.session_state.adjusters_cfg)),format_func=lambda i: st.session_state.adjusters_cfg[i]['adjuster_id'],key='adjuster_remove')
        if st.button('Remove selected adjuster'):
            st.session_state.adjusters_cfg.pop(adjuster_remove); st.rerun()

st.divider()
if st.button('Run simulation', type='primary', disabled=not st.session_state.machines_cfg or not st.session_state.adjusters_cfg):
    payload={'machines':st.session_state.machines_cfg,'adjusters':st.session_state.adjusters_cfg,'duration':duration,'warmup':0,'seed':int(seed),'save':True}
    try:
        response=requests.post(api+'/simulate',json=payload,timeout=120); response.raise_for_status(); st.session_state.result=response.json()
    except Exception as e: st.error(f'Could not run simulation: {e}')
if 'result' in st.session_state:
    r=st.session_state.result
    st.subheader('Simulation result')
    a,b,c,d=st.columns(4); a.metric('Machine efficiency',f"{r['machine_utilization']:.1%}"); b.metric('Adjuster utilization',f"{r['adjuster_utilization']:.1%}"); c.metric('Total failures',r['failures']); d.metric('Machines waiting',r['waiting_machines'])
    st.caption('Machine efficiency = running seconds / total run seconds. Adjuster utilization = repair-busy seconds / total run seconds.')
    st.subheader('Machine category summary')
    cats=pd.DataFrame(r.get('categories',{})).T.reset_index().rename(columns={'index':'category','machine_utilization':'efficiency'})
    if not cats.empty: st.dataframe(cats.style.format({'efficiency':'{:.1%}'}),use_container_width=True,hide_index=True)
    st.subheader('Per-machine efficiency')
    machines=pd.DataFrame(r.get('machines',[]))
    if not machines.empty: st.dataframe(machines.style.format({'efficiency_percent':'{:.1f}%'}),use_container_width=True,hide_index=True)
