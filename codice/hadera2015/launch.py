import gurobipy as gp
import model
from functions import draw_gantt_chart

hedera_model = model.get_hedera_model()
hedera_model.optimize()

# Draw Gantt chart
print("\nGenerating Gantt chart...")
draw_gantt_chart(hedera_model)



