import model
import data
from gurobipy import GRB
import functions

for c in data.casting_lines:
    mdl = model.get_optimal_power_profiles_simplified(c)
    mdl.setParam("MIPGap", 1.10)
    # mdl.setParam("NoRelHeurTime", 30)
    mdl.optimize()
    if mdl.status == GRB.OPTIMAL:
        print(mdl.ObjVal)
        functions.plot_total_power(mdl)
        # functions.plot_gantt_schedule(mdl)
        functions.plot_power_per_furnace(mdl)
        # functions.print_stage_info(mdl)
        for k in range(1):
            pass
            #functions.print_power_details_for_timestep(mdl, k)
    # se non è feasible calcolo IIS
    else:
        mdl.computeIIS()
        mdl.write('model.ilp')
