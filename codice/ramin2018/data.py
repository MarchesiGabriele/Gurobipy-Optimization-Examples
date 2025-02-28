# SETS
furnaces = ['F1', 'F2', 'F3', 'F4']
# furnaces = ['F1']
power_lines = ['L1', 'L2']
# power_lines = ['L1']
casting_lines = ['C1']
jobs = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']

FC = {
    'C1': ['F1', 'F2', 'F3', 'F4']
    # 'C1': ['F1']
}
FL = {
    'L1': ['F1', 'F2'],
    'L2': ['F3', 'F4']
    # 'L1': ['F1'],
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

time_grid = [i for i in range(0, 24*60//5)] # 5 min per ogni step

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
            'LOADING': 8e6,
            'PRIMARY_HEATING': 8e6,
            'CHARGE_MELTING': 8e6,
            'MELTING': 8e6,
            'ANALYSIS': 8e6,
            'OVERHEATING': 8e6,
            'TAPPING': 8e6,
        } for j in range(1,8)
    } for i in range(1,5)
}

# energia in kWh
E_hat = {
    f'F{i}': {
        f'T{j}': {
            'LOADING': 0,
            'PRIMARY_HEATING': 6.122e3,
            'CHARGE_MELTING': 30.194e3,
            'MELTING': 7.768e3,
            'ANALYSIS': 0,
            'OVERHEATING': 3.402e3,
            'TAPPING': 0,
        } for j in range(1,8)
    } for i in range(1,5)
}

# tempo in secondi
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
    '0': 23, '1': 22, '2': 21, '3': 21, '4': 22, '5': 23,
    '6': 27, '7': 32, '8': 33, '9': 34, '10': 29, '11': 29,
    '12': 28, '13': 28, '14': 28, '15': 27, '16': 27, '17': 33,
    '18': 34, '19': 32, '20': 31, '21': 29, '22': 25, '23': 23
}

# prezzi orari in €/kWh
prezzi_orari = {
    time_grid[i]: prezzi_orari_base[str(i//12)]
    for i in range(len(time_grid))
}











