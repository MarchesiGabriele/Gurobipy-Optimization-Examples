import gurobipy as gp
import model
from gurobipy import GRB
from functions import draw_gantt_chart, plot_energy_prices, plot_flows
import sys

hedera_model = model.get_hedera_full_model_simplified()
hedera_model.optimize()

# do IIS if the model is infeasible
if hedera_model.Status == GRB.INFEASIBLE:
    hedera_model.computeIIS()
    hedera_model.write('hedera_model.ilp')
    exit()

# Draw Gantt chart
print("\nGenerating Gantt chart...")
draw_gantt_chart(hedera_model)

# Plot energy prices
print("\nGenerating energy prices plot...")
plot_energy_prices(hedera_model)

# Plot flows
print("\nGenerating energy flows plot...")
# plot_flows(hedera_model)



