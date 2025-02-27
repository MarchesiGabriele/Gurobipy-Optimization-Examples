import model
import data


for c in data.casting_lines:
    mdl = model.get_optimal_power_profiles_simplified(c)
    mdl.optimize()
    print(mdl.objVal)
    # salvo i
