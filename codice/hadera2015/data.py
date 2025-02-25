import numpy as np

# SETS
heat = [f'P{i}' for i in range(1,21)] # TODO: CHANGE BACK TO 21
equipment = ['EAF1', 'EAF2', 'AOD1', 'AOD2', 'LF1', 'LF2', 'CC1', 'CC2'] 
production_stage = ['EAF', 'AOD', 'LF', 'CC']
stage_machines_mapping = {
    'EAF': ['EAF1', 'EAF2'],
    'AOD': ['AOD1', 'AOD2'],
    'LF': ['LF1', 'LF2'],
    'CC': ['CC1', 'CC2'],
}
heat_groups = ['HG1', 'HG2', 'HG3', 'HG4', 'HG5'] # TODO: ADD BACK HEAT GROUPS HG1, HG2, HG3, HG4, HG5
sub_heat_groups = {'HG1': ['P1', 'P2', 'P3'], # TODO add back P2, P3
                   'HG2': ['P4', 'P5', 'P6', 'P7'],
                   'HG3': ['P8', 'P9', 'P10', 'P11', 'P12'],
                   'HG4': ['P13', 'P14', 'P15', 'P16'],
                   'HG5': ['P17', 'P18', 'P19', 'P20']
}
last_sub_heat_group = {'HG1': 'P3', 'HG2': 'P7', 'HG3': 'P12', 'HG4': 'P16', 'HG5': 'P20'}
first_sub_heat_group = {'HG1': 'P1', 'HG2': 'P4', 'HG3': 'P8', 'HG4': 'P13', 'HG5': 'P17'}
time_interval = [f'{i}' for i in range(1, 25)]
node = [f'{i}' for i in range(1, 8)]
pur = ['1', '2','3']
dem = ['7'] 
gen = ['4']
bal = ['5'] 
sale = ['6']
arc = {'1':['5'], 
       '2':['5'], 
       '3':['5'], 
       '4':['5'], 
       '5':['6','7'], 
       '6':[], 
       '7':[], 
       }


# PARAMETERS
teta = {p: {'EAF1':85, 'EAF2':85, 'AOD1':8, 'AOD2':8, 'LF1':45, 'LF2':45, 'CC1':60, 'CC2':60} for p in heat}
tmin = {'EAF1':{'AOD1':10, 'AOD2':25, 'LF1':0, 'LF2':0, 'CC1':0, 'CC2':0}, 
        'EAF2':{'AOD1':25, 'AOD2':10, 'LF1':0, 'LF2':0, 'CC1':0, 'CC2':0}, 
        'AOD1':{'EAF1':0, 'EAF2':0, 'LF1':4, 'LF2':20, 'CC1':0, 'CC2':0}, 
        'AOD2':{'EAF1':0, 'EAF2':0, 'LF1':20, 'LF2':4, 'CC1':0, 'CC2':0}, 
        'LF1':{'EAF1':0, 'EAF2':0, 'AOD1':0, 'AOD2':0, 'CC1':20, 'CC2':45}, 
        'LF2':{'EAF1':0, 'EAF2':0, 'AOD1':0, 'AOD2':0, 'CC1':45, 'CC2':20}
        }
tmax = {p:{'EAF':60, 'AOD':90, 'LF':60} for p in heat}
tsetup = {'EAF1': 9, 'EAF2': 9, 'AOD1': 5, 'AOD2': 5, 'LF1': 15, 'LF2': 5, 'CC1': 50, 'CC2': 70}
tau = {t:(int(t)-1)*60 for t in time_interval}
flowmin = {s: {  '1': {'5':30},
                    '2': {'5':0},
                    '3': {'5':0},
                    '4': {'5':0},
                    '5': {'6':0, 
                          '7':0
                          },
                  } for s in time_interval}
flowmax = {s: {  '1': {'5':30},
                    '2': {'5':100},
                    '3': {'5':100},
                    '4': {'5':40},
                    '5': {'6': 270,  # TODO: MODIFICARE
                          '7':270   # TODO: MODIFICARE
                          },
                  } for s in time_interval}

load_curve = {
    '1': 170,
    '2': 144.5,
    '3': 167.17,
    '4': 147.33,
    '5': 151.03,
    '6': 177,
    '7': 157.1,
    '8': 151.97,
    '9': 177,
    '10': 153.37,
    '11': 152.9,
    '12': 177,
    '13': 151.5,
    '14': 168.5,
    '15': 163.15,
    '16': 94.83,
    '17': 12.02,
    '18': 14,
    '19': 8.98,
    '20': 7.00,
    '21': 1.98,
    '22': 0,
    '23': 0,
    '24': 0
}

power_consumption = {p: {'EAF1':85, 'EAF2':85, 'AOD1':2, 'AOD2':2, 'LF1':2, 'LF2':2, 'CC1':7, 'CC2':7} for p in heat}




costi_energia = {s: {  '1': {'5':None},
                    '2': {'5':None},
                    '3': {'5':None},
                    '4': {'5':61},
                  } for s in time_interval}


costi_energia = {str(i+1): {'1': {'5':None}, '2': {'5':None}, '3': {'5':None}, '4': {'5':61}, '5': {'6':None}} for i in range(24)}

costi_energia['1']['1']['5'] = 60
costi_energia['1']['2']['5'] = 65
costi_energia['1']['3']['5'] = 100
costi_energia['1']['5']['6'] = 100

costi_energia['2']['1']['5'] = 60
costi_energia['2']['2']['5'] = 65
costi_energia['2']['3']['5'] = 80
costi_energia['2']['5']['6'] = 80

costi_energia['3']['1']['5'] = 60
costi_energia['3']['2']['5'] = 65
costi_energia['3']['3']['5'] = 75
costi_energia['3']['5']['6'] = 75

costi_energia['4']['1']['5'] = 60
costi_energia['4']['2']['5'] = 65
costi_energia['4']['3']['5'] = 61
costi_energia['4']['5']['6'] = 61

costi_energia['5']['1']['5'] = 60
costi_energia['5']['2']['5'] = 65
costi_energia['5']['3']['5'] = 80
costi_energia['5']['5']['6'] = 80

costi_energia['6']['1']['5'] = 60
costi_energia['6']['2']['5'] = 65
costi_energia['6']['3']['5'] = 100
costi_energia['6']['5']['6'] = 100

costi_energia['7']['1']['5'] = 60
costi_energia['7']['2']['5'] = 65
costi_energia['7']['3']['5'] = 120
costi_energia['7']['5']['6'] = 120

costi_energia['8']['1']['5'] = 60
costi_energia['8']['2']['5'] = 65
costi_energia['8']['3']['5'] = 180
costi_energia['8']['5']['6'] = 180

costi_energia['9']['1']['5'] = 60
costi_energia['9']['2']['5'] = 65
costi_energia['9']['3']['5'] = 180
costi_energia['9']['5']['6'] = 180

costi_energia['10']['1']['5'] = 60
costi_energia['10']['2']['5'] = 65
costi_energia['10']['3']['5'] = 600
costi_energia['10']['5']['6'] = 600

costi_energia['11']['1']['5'] = 60
costi_energia['11']['2']['5'] = 65
costi_energia['11']['3']['5'] = 200
costi_energia['11']['5']['6'] = 200

costi_energia['12']['1']['5'] = 60
costi_energia['12']['2']['5'] = 65
costi_energia['12']['3']['5'] = 160
costi_energia['12']['5']['6'] = 160

costi_energia['13']['1']['5'] = 60
costi_energia['13']['2']['5'] = 90
costi_energia['13']['3']['5'] = 120
costi_energia['13']['5']['6'] = 120

costi_energia['14']['1']['5'] = 60
costi_energia['14']['2']['5'] = 90
costi_energia['14']['3']['5'] = 90
costi_energia['14']['5']['6'] = 90

costi_energia['15']['1']['5'] = 60
costi_energia['15']['2']['5'] = 90
costi_energia['15']['3']['5'] = 90
costi_energia['15']['5']['6'] = 90

costi_energia['16']['1']['5'] = 60
costi_energia['16']['2']['5'] = 90
costi_energia['16']['3']['5'] = 100
costi_energia['16']['5']['6'] = 100

costi_energia['17']['1']['5'] = 60
costi_energia['17']['2']['5'] = 90
costi_energia['17']['3']['5'] = 100
costi_energia['17']['5']['6'] = 100

costi_energia['18']['1']['5'] = 60
costi_energia['18']['2']['5'] = 90
costi_energia['18']['3']['5'] = 120
costi_energia['18']['5']['6'] = 120

costi_energia['19']['1']['5'] = 60
costi_energia['19']['2']['5'] = 90
costi_energia['19']['3']['5'] = 160
costi_energia['19']['5']['6'] = 160

costi_energia['20']['1']['5'] = 60
costi_energia['20']['2']['5'] = 90
costi_energia['20']['3']['5'] = 160
costi_energia['20']['5']['6'] = 160

costi_energia['21']['1']['5'] = 60
costi_energia['21']['2']['5'] = 90
costi_energia['21']['3']['5'] = 120
costi_energia['21']['5']['6'] = 120

costi_energia['22']['1']['5'] = 60
costi_energia['22']['2']['5'] = 90
costi_energia['22']['3']['5'] = 100
costi_energia['22']['5']['6'] = 100

costi_energia['23']['1']['5'] = 60
costi_energia['23']['2']['5'] = 90
costi_energia['23']['3']['5'] = 90
costi_energia['23']['5']['6'] = 90

costi_energia['24']['1']['5'] = 60
costi_energia['24']['2']['5'] = 90
costi_energia['24']['3']['5'] = 80
costi_energia['24']['5']['6'] = 80

# Vector of energy costs for supplier 3
costi_energia_3 = [
    100,  # 1
    80,   # 2
    75,   # 3
    61,   # 4
    80,   # 5
    100,  # 6
    120,  # 7
    180,  # 8
    180,  # 9
    600,  # 10
    200,  # 11
    160,  # 12
    120,  # 13
    90,   # 14
    90,   # 15
    100,  # 16
    100,  # 17
    120,  # 18
    160,  # 19
    160,  # 20
    120,  # 21
    100,  # 22
    90,   # 23
    80    # 24
]

