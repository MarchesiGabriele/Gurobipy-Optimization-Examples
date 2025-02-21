import gurobipy as gp
import model

# TODO: change params from dict to pd.series (o simile)

hedera_model = model.get_hedera_model()
hedera_model.optimize()






