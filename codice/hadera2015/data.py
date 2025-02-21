import numpy as np

# SETS
heat = [f'P{i}' for i in range(1,21)]
equipment = ['EAF1', 'EAF2', 'AOD1', 'AOD2', 'LF1', 'LF2', 'CC1', 'CC2'] 
production_stage = ['EAF', 'AOD', 'LF', 'CC']
stage_machines_mapping = {
    'EAF': ['EAF1', 'EAF2'],
    'AOD': ['AOD1', 'AOD2'],
    'LF': ['LF1', 'LF2'],
    'CC': ['CC1', 'CC2'],
}
heat_groups = ['HG1', 'HG2', 'HG3', 'HG4', 'HG5']
sub_heat_groups = {'HG1': ['P1', 'P2', 'P3'],
                   'HG2': ['P4', 'P5', 'P6', 'P7'],
                   'HG3': ['P8', 'P9', 'P10', 'P11', 'P12'],
                   'HG4': ['P13', 'P14', 'P15', 'P16'],
                   'HG5': ['P17', 'P18', 'P19', 'P20']
}
last_sub_heat_group = {'HG1': 'P3', 'HG2': 'P7', 'HG3': 'P12', 'HG4': 'P16', 'HG5': 'P20'}
first_sub_heat_group = {'HG1': 'P1', 'HG2': 'P4', 'HG3': 'P8', 'HG4': 'P13', 'HG5': 'P17'}


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
tau = {p: {'EAF1':85, 'EAF2':85, 'AOD1':2, 'AOD2':2, 'LF1':2, 'LF2':2, 'CC1':7, 'CC2':7} for p in heat}