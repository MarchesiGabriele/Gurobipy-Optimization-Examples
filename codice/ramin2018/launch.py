import model
import data
from gurobipy import GRB

for c in data.casting_lines:
    mdl = model.get_optimal_power_profiles_simplified(c)
    mdl.optimize()
    if mdl.status == GRB.OPTIMAL:
        print(mdl.ObjVal)
    # se non è feasible calcolo IIS
    else:
        mdl.computeIIS()
        mdl.write('model.ilp')
