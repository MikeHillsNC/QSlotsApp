import numpy as np
import pandas as pd
from IPython.display import display #mth

np.random.seed(100)

ARR=0
DEP=1


EVCLOCK=0
EVTYPE=1
EVAGENT=2
EVTIME=3
EVINDEX=4

events = pd.DataFrame(columns=['clock','type','ev_agent','time'])
#print (df)

while True:
    clock=0.0
    for i in range(11):
        nextArrival=int((-np.log(1-(np.random.uniform(low=0.0,high=1.0))) * 16))
        clock+=nextArrival
        #events.append([clock,ARR,0,nextArrival])
        #s1=pd.Series([clock,ARR,0,nextArrival])
        s1 = pd.DataFrame({'clock': [clock],
                            'type' : [ARR],
                            'ev_agent' : [0],
                            'time':[nextArrival]})
        events=pd.concat([events,s1])

    #print(events)
    
    clock=0.0
    for i in range(11):
        nextDep=int((-np.log(1-(np.random.uniform(low=0.0,high=1.0))) * 60))
        iAgent=np.random.choice([1,2,3,4,5])
        clock+=nextDep
        #events.append([clock,DEP,iAgent,nextDep])
        # s1=pd.Series([clock,DEP,iAgent,nextDep])
        # pd.concat([df,s1],ignore_index=True)        
        s1 = pd.DataFrame({'clock': [clock],
                            'type' : [DEP],
                            'ev_agent' : [iAgent],
                            'time':[nextDep]})
        events=pd.concat([events,s1])

    #print(events) 

    events.sort_values(by=['clock'], inplace=True)
    print(events)
    
    numArrEvents=len(events.loc[events.type==ARR])
    df=events.query('type==0')
    maxArrTime=df['clock'].max()
   
    pass 
 

pass