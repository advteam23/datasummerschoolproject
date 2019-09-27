# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 14:26:23 2019

@author: MV
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 07:25:47 2019

@author: MV
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 14:45:46 2019

@author: MV
"""
import numpy as np
import pandas as pd

#learning curve
gamma = 0.4
alpha = 0.02

location_to_state = {'beg': 0,
                     'spend_day1': 1,
                     'increase1': 2,
                     'increase1.2': 3,
                     'notspend_day1': 4,
                     'free_flowI': 5,
                     'free_flowII': 6,
                     'end_day1': 7,
                     'spend_day2': 8,
                     'increase2.1': 9,
                     'increase2.2': 10,
                     'notspend_day2': 11,
                     'free_flowIV':12,
                     'free_flowV':13,
                     'end_day2':14
                     
                     
                     }
nothing=5+0
#coeLand1=0.4179
#coeReact1 =0.5362 
#coeClick1 =0.1674
coeLand1=0.46801
coeReact1 =1.79781
coeClick1 =3
coeLand2=4
coeReact2 =1.79781
coeClick2 =0.47247

budget=1
#targeted_cost = 10
#covClick1=0.51479
#covLand1=0.01352
#covReact1=-0.41653
#cpc= targeted_cost/targeted_conversion
#budget formula: budget = scale*conversion
data_store=[]
result_store=[]
state_to_location = {state: location for location, state in location_to_state.items()}

def route(starting_location,ending_location):
    
    #day2_increase = (budget*coeClick1+budget*coeReact1+budget*coeLand1)*cpc
    #function = (budget*0.4285) + budget*0.2686 + 1.0910*budget
    actions = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
    R = np.array([[0,-1,0,0,1,0,0,0,0,0,0,0,0,0,0], #1 beg
              [0,0,coeClick1,0,0,0,0,0,0,0,0,0,0,0,0], #2 spend1
              [0,0,0,coeReact1,0,0,0,0,0,0,0,0,0,0,0], #3 inc1.1
              [0,0,0,0,0,coeLand1,0,0,0,0,0,0,0,0,0], #4 inc1.2
              [0,0,0,0,0,0.01,0,0,0,0,0,0,0,0,0], #5 notspend1
              [0,0,0,0,0,0,0.01,0,0,0,0,0,0,0,0], #6 freefall1.1
              [0,0,0,0,0,0,0,0.01,0,0,0,0,0,0,0], #7 freefall1.2
              [0,0,0,0,0,0,0,0,-1,0,0,1,0,0,0], #8 end1
              [0,0,0,0,0,0,0,0,0,coeClick2,0,0,0,0,0], #9 spend2
              [0,0,0,0,0,0,0,0,0,0,coeReact1,0,0,0,0], #10 inc2.1
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,coeLand2], #11 inc2.2
              [0,0,0,0,0,0,0,0,0,0,0,0,0.01,0,0], #12 notspend_day2
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0.01,0], #13 same2.1
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.01], #14 same2.2
              [0,0,0,0,0,0,0,0,0,0,1,0,0,1,0] #15 end2
              
              
              
              
              
              ])

    R_new = np.copy(R)
    ending_state = location_to_state[ending_location]
    R_new[ending_state, ending_state] = 1000
    Q = np.array(np.zeros([15,15]))
    for i in range(1000):
        current_state = np.random.randint(0,15)
        playable_actions = []
        for j in range(15):
            if R_new[current_state, j] != 0:
                playable_actions.append(j)
        next_state = np.random.choice(playable_actions)
        TD = R_new[current_state, next_state] + gamma * Q[next_state, np.argmax(Q[next_state,])] - Q[current_state, next_state]
        Q[current_state, next_state] = Q[current_state, next_state] + alpha * TD
        print(Q)
    route = [starting_location]
    next_location = starting_location
    while (next_location != ending_location):
        starting_state = location_to_state[starting_location]
        next_state = np.argmax(Q[starting_state,])
        next_location = state_to_location[next_state]
        route.append(next_location)
        starting_location = next_location

    data_store.append(route)
    return route

def best_route(starting_location, intermediary_location, ending_location):
    return route(starting_location, intermediary_location) + route(intermediary_location, ending_location)[1:]

print('Route:')
route('beg','end_day2')



