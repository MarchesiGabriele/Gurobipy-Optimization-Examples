# SETS
furnaces = ['F1', 'F2', 'F3', 'F4']
power_lines = ['L1', 'L2']
casting_lines = ['C1']
jobs = ['J1', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7']

FC = {
    'C1': ['F1', 'F2', 'F3', 'F4']
}
FL = {
    'L1': ['F1', 'F2'],
    'L2': ['F3', 'F4']
}
M  = {
    'F1': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'],
    'F2': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'],
    'F3': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'],
    'F4': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'],
}

stages = ['LOADING', 'PRIMARY_HEATING', 'CHARGE_MELTING', 'MELTING', 'ANALYSIS', 'OVERHEATING', 'TAPPING']
energy_based_stages = ['PRIMARY_HEATING', 'CHARGE_MELTING', 'MELTING', 'OVERHEATING']
time_based_stages = ['LOADING', 'ANALYSIS', 'TAPPING']

time_grid = [i*5 for i in range(24*60//5)]

pminstage = {
    f'F{i}': {
        f'T{j}': {
            'LOADING': 2,
            'PRIMARY_HEATING': 2,
            'CHARGE_MELTING': 2,
            'MELTING': 2,
            'ANALYSIS': 2,
            'OVERHEATING': 2,
            'TAPPING': 2,
        } for j in range(1,8)
    } for i in range(1,5)
}

pmaxstage = {
    f'F{i}': {
        f'T{j}': {
            'LOADING': 8,
            'PRIMARY_HEATING': 8,
            'CHARGE_MELTING': 8,
            'MELTING': 8,
            'ANALYSIS': 8,
            'OVERHEATING': 8,
            'TAPPING': 8,
        } for j in range(1,8)
    } for i in range(1,5)
}

E_hat = {
    f'F{i}': {
        f'T{j}': {
            'LOADING': 0,
            'PRIMARY_HEATING': 6122000,
            'CHARGE_MELTING': 30194000,
            'MELTING': 7768000,
            'ANALYSIS': 0,
            'OVERHEATING': 3402000,
            'TAPPING': 0,
        } for j in range(1,8)
    } for i in range(1,5)
}

stage_time = {
    f'F{i}': {
        f'T{j}': {
            'LOADING': 60,
            'PRIMARY_HEATING': 0,
            'CHARGE_MELTING': 0,
            'MELTING': 0,
            'ANALYSIS': 40,
            'OVERHEATING': 0,
            'TAPPING': 0,
        } for j in range(1,8)
    } for i in range(1,5)
}

# casting_lines = []
# melting_furnaces = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8']
# power_lines = ['L1', 'L2', 'L3']
# casting_lines = ['C1', 'C2', 'C3', 'C4']
# power_line_furnaces  = {
#     'L1':['M1', 'M2', 'M3', 'M4'],
#     'L2':['M5', 'M6'],
#     'L3':['M7', 'M8']
# } # melting furnaces raggruppate per power line
# casting_line_furnaces  = {
# } # melting furnaces raggruppate per casting line, fornito da BS-LA
# time_grid = []
# stages = ['LOADING', 'PRIMARY_HEATING', 'CHARGE_MELTING', 'MELTING', 'ANALYSIS', 'OVERHEATING', 'TAPPING']
# energy_based_stages = ['PRIMARY_HEATING', 'CHARGE_MELTING', 'MELTING', 'OVERHEATING']
# time_based_stages = ['LOADING', 'ANALYSIS', 'TAPPING']
# melt_jobs= {} # lista di jobs per ciascuna melting furnace  fornito da BS-LA

# actual_stage_energy = []
# min_stage_energy = []











