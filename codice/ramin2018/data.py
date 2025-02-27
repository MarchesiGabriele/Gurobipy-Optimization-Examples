# SETS
furnaces = ['F1', 'F2', 'F3', 'F4']
power_lines = ['L1', 'L2']
casting_lines = ['C1']
jobs = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']

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

time_grid = [f'{i}' for i in range(0, 24*60//5)] # 5 min per ogni step

pminstage = {
    f'F{i}': {
        f'T{j}': {
            'LOADING': 0,
            'PRIMARY_HEATING': 0,
            'CHARGE_MELTING': 0,
            'MELTING': 0,
            'ANALYSIS': 0,
            'OVERHEATING': 0,
            'TAPPING': 0,
        } for j in range(1,8)
    } for i in range(1,5)
}

pmaxstage = {
    f'F{i}': {
        f'T{j}': {
            'LOADING': 800,
            'PRIMARY_HEATING': 800,
            'CHARGE_MELTING': 800,
            'MELTING': 800,
            'ANALYSIS': 800,
            'OVERHEATING': 800,
            'TAPPING': 800,
        } for j in range(1,8)
    } for i in range(1,5)
}

E_hat = {
    f'F{i}': {
        f'T{j}': {
            'LOADING': 0,
            'PRIMARY_HEATING': 6.122,
            'CHARGE_MELTING': 30.194,
            'MELTING': 7.768,
            'ANALYSIS': 0,
            'OVERHEATING': 3.402,
            'TAPPING': 0,
        } for j in range(1,8)
    } for i in range(1,5)
}

stage_time = {
    f'F{i}': {
        f'T{j}': {
            'LOADING': 60*60,
            'PRIMARY_HEATING': 0,
            'CHARGE_MELTING': 0,
            'MELTING': 0,
            'ANALYSIS': 40*60,
            'OVERHEATING': 0,
            'TAPPING': 0,
        } for j in range(1,8)
    } for i in range(1,5)
}

prezzi_orari_base = {
    '0': 22.5, '1': 22, '2': 21.8, '3': 21.8, '4': 22, '5': 22.5,
    '6': 23, '7': 27, '8': 31, '9': 32.5, '10': 33.5, '11': 33.5,
    '12': 33.5, '13': 33.5, '14': 33.5, '15': 33.5, '16': 29.5, '17': 32,
    '18': 31, '19': 30, '20': 29, '21': 27, '22': 23, '23': 22.5
}

prezzi_orari = {
    time_grid[i]: prezzi_orari_base[str(i//12)]
    for i in range(len(time_grid))
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











