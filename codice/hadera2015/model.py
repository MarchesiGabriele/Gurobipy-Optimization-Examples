import gurobipy as gp
from gurobipy import GRB
import data

# Helper function to get product index
def _get_product_index(p: str) -> int:
    return int(p.replace('P', ''))

def get_hedera_schedulingmodel() -> gp.Model:
    mdl = gp.Model('hedera')

    # SETS
    P = data.heat # products
    M = data.equipment # machines
    ST = data.production_stage
    SM = data.stage_machines_mapping
    HG = data.heat_groups
    HGP = data.sub_heat_groups
    L = data.last_sub_heat_group    
    F = data.first_sub_heat_group


    # PARAMETERS
    teta = data.teta
    tmin = data.tmin
    tmax = data.tmax
    tsetup = data.tsetup
    HORIZON = 24*60

    # DECISION VARIABLES
    X = mdl.addVars(M,P, vtype=GRB.BINARY, name='product_to_machine')
    tf = mdl.addVars(M,P, vtype=GRB.CONTINUOUS, name='time_finish')
    ts = mdl.addVars(M,P, vtype=GRB.CONTINUOUS, name='time_start')
    tfstage = mdl.addVars(P,ST, vtype=GRB.CONTINUOUS, name='time_finish_stage') 
    tsstage = mdl.addVars(P,ST, vtype=GRB.CONTINUOUS, name='time_start_stage') 
    w = mdl.addVars(P, ST, vtype=GRB.CONTINUOUS, name='slack_after_stage') 
    V = mdl.addVars(ST, P, P, vtype=GRB.BINARY, name='precedence')


    # SCHEDULING CONSTRAINTS
    mdl.addConstrs((gp.quicksum(X[m,p] for m in SM[st]) == 1 for p in P for st in ST), name='(1)')
    mdl.addConstrs((tf[m,p] == ts[m,p] + X[m,p]*teta[p][m] for m in M for p in P), name='(2)')
    mdl.addConstrs((ts[m,p] <= HORIZON*X[m,p] for m in M for p in P), name='(3)') 
    mdl.addConstrs((tsstage[p,st] == gp.quicksum(ts[m,p] for m in SM[st]) for p in P for st in ST), name='(4)')
    mdl.addConstrs((tfstage[p,st] == gp.quicksum(tf[m,p] for m in SM[st]) for p in P for st in ST), name='(5)')
    mdl.addConstrs((tsstage[p,ST[i+1]] == tfstage[p,ST[i]] + w[p,ST[i]] for p in P for i in range(len(ST)-1)), name='(6)') # Constraint linking consecutive stages
    mdl.addConstrs((tmin[m][m1]*(X[m,p]+X[m1,p]-1) <= w[p,ST[i]] for p in P 
                                                                    for i in range(len(ST)-1)
                                                                        for m in M if m in SM[ST[i]]
                                                                            for m1 in M if m1 in SM[ST[i+1]]), name='(7.1)') 
    mdl.addConstrs((w[p,st] <= tmax[p][st] for p in P 
                                                for st in ST if st != 'CC'), name='(7.2)') 
    mdl.addConstrs((V[st, p, p1] + V[st, p1, p] == 1 for st in ST 
                                                        for p in P 
                                                            for p1 in P if _get_product_index(p) < _get_product_index(p1)), name='(8)') 
    mdl.addConstrs((V[ST[i], p, p1] == V[ST[i+1], p, p1] for i in range(len(ST)-1) 
                                                            for p in P 
                                                                for p1 in P if _get_product_index(p) < _get_product_index(p1)), name='(9)')
    mdl.addConstrs((ts[m,p1] >= tf[m,p] + tsetup[m] - (HORIZON+ tsetup[m])*(3-V[st,p,p1]-X[m,p]-X[m,p1]) for p in P 
                                                                                                            for p1 in P if _get_product_index(p) != _get_product_index(p1) 
                                                                                                                for st in ST if st != 'CC'
                                                                                                                    for m in M if m in SM[st]), name='(10)')
    mdl.addConstrs((ts[m,p1] >= tf[m,p] - HORIZON*(3-V[st,p,p1]-X[m,p]-X[m,p1]) for p in P 
                                                                                    for p1 in P if _get_product_index(p) != _get_product_index(p1)
                                                                                        for st in ST if st == 'CC'
                                                                                            for m in M if m in SM[st]), name='(11)')
    mdl.addConstrs((ts[m,F[hg]] >= tf[m,L[hg]] + tsetup[m] - (HORIZON+ tsetup[m])*(3-V[st,L[hg],F[hg]]-X[m,L[hg]]-X[m,F[hg]]) for hg in HG if L[hg] != F[hg]
                                                                                                                                for st in ST if st == 'CC'
                                                                                                                                    for m in M if m in SM[st]), name='(12)') # TODO è correto che l'heatgroup sia lo stesso per L ed F
    mdl.addConstrs((X[m,f'P{_get_product_index(p)}'] == X[m, f'P{_get_product_index(p)+1}'] for hg in HG 
                                                                                                for p in HGP[hg] if p not in L[hg] 
                                                                                                    for m in M), name='(13, non è quello del paper)')                                                                                                                               
    mdl.addConstrs((tsstage[P[i+1], st] == tfstage[P[i], st] for hg in HG for i in range(len(P)-1) if P[i] != L[hg] for st in ST if st == 'CC'), name='(14)')    
    mdl.addConstrs((V[st,p,p1] == 1 for hg in HG for p in P if p in HGP[hg] for p1 in P if _get_product_index(p) < _get_product_index(p1) and p1 in HGP[hg] for st in ST ), name='(15)') # TODO: check insiemi (devo mettere anche HG ???) (la precedenza è su prodotti di uno stesso HG, non su quelli totali)
    mdl.addConstrs((V[st,p,p1] == 0 for p in P for p1 in P if _get_product_index(p) == _get_product_index(p1) for st in ST), name='(16)')  

    # OBJECTIVE FUNCTION
    mdl.setObjective(gp.quicksum(ts[m, p] for m in M for p in P), GRB.MINIMIZE) 
    return mdl



def get_hedera_full_model() -> gp.Model:
    mdl = gp.Model('hedera_full')

    # SETS
    P = data.heat # products
    M = data.equipment # machines
    ST = data.production_stage
    SM = data.stage_machines_mapping
    HG = data.heat_groups
    HGP = data.sub_heat_groups
    L = data.last_sub_heat_group    
    F = data.first_sub_heat_group
    S = data.time_interval


    # PARAMETERS
    teta = data.teta
    tmin = data.tmin
    tmax = data.tmax
    tsetup = data.tsetup
    tau = data.tau
    HORIZON = 24*60

    # DECISION VARIABLES
    X = mdl.addVars(M,P, vtype=GRB.BINARY, name='product_to_machine')
    tf = mdl.addVars(M,P, vtype=GRB.CONTINUOUS, name='time_finish')
    ts = mdl.addVars(M,P, vtype=GRB.CONTINUOUS, name='time_start')
    tfstage = mdl.addVars(P,ST, vtype=GRB.CONTINUOUS, name='time_finish_stage') 
    tsstage = mdl.addVars(P,ST, vtype=GRB.CONTINUOUS, name='time_start_stage') 
    w = mdl.addVars(P, ST, vtype=GRB.CONTINUOUS, name='slack_after_stage') 
    V = mdl.addVars(ST, P, P, vtype=GRB.BINARY, name='precedence')
    ys = mdl.addVars(P, ST, S, vtype=GRB.BINARY, name='product_to_time_interval_start')
    yf = mdl.addVars(P, ST, S, vtype=GRB.BINARY, name='product_to_time_interval_finish')   

    # SCHEDULING CONSTRAINTS
    mdl.addConstrs((gp.quicksum(X[m,p] for m in SM[st]) == 1 for p in P for st in ST), name='(1)')
    mdl.addConstrs((tf[m,p] == ts[m,p] + X[m,p]*teta[p][m] for m in M for p in P), name='(2)')
    mdl.addConstrs((ts[m,p] <= HORIZON*X[m,p] for m in M for p in P), name='(3)') 
    mdl.addConstrs((tsstage[p,st] == gp.quicksum(ts[m,p] for m in SM[st]) for p in P for st in ST), name='(4)')
    mdl.addConstrs((tfstage[p,st] == gp.quicksum(tf[m,p] for m in SM[st]) for p in P for st in ST), name='(5)')
    mdl.addConstrs((tsstage[p,ST[i+1]] == tfstage[p,ST[i]] + w[p,ST[i]] for p in P for i in range(len(ST)-1)), name='(6)') # Constraint linking consecutive stages
    mdl.addConstrs((tmin[m][m1]*(X[m,p]+X[m1,p]-1) <= w[p,ST[i]] for p in P 
                                                                    for i in range(len(ST)-1)
                                                                        for m in M if m in SM[ST[i]]
                                                                            for m1 in M if m1 in SM[ST[i+1]]), name='(7.1)') 
    mdl.addConstrs((w[p,st] <= tmax[p][st] for p in P 
                                                for st in ST if st != 'CC'), name='(7.2)') 
    mdl.addConstrs((V[st, p, p1] + V[st, p1, p] == 1 for st in ST 
                                                        for p in P 
                                                            for p1 in P if _get_product_index(p) < _get_product_index(p1)), name='(8)') 
    mdl.addConstrs((V[ST[i], p, p1] == V[ST[i+1], p, p1] for i in range(len(ST)-1) 
                                                            for p in P 
                                                                for p1 in P if _get_product_index(p) < _get_product_index(p1)), name='(9)')
    mdl.addConstrs((ts[m,p1] >= tf[m,p] + tsetup[m] - (HORIZON+ tsetup[m])*(3-V[st,p,p1]-X[m,p]-X[m,p1]) for p in P 
                                                                                                            for p1 in P if _get_product_index(p) != _get_product_index(p1) 
                                                                                                                for st in ST if st != 'CC'
                                                                                                                    for m in M if m in SM[st]), name='(10)')
    mdl.addConstrs((ts[m,p1] >= tf[m,p] - HORIZON*(3-V[st,p,p1]-X[m,p]-X[m,p1]) for p in P 
                                                                                    for p1 in P if _get_product_index(p) != _get_product_index(p1)
                                                                                        for st in ST if st == 'CC'
                                                                                            for m in M if m in SM[st]), name='(11)')
    mdl.addConstrs((ts[m,F[hg]] >= tf[m,L[hg]] + tsetup[m] - (HORIZON+ tsetup[m])*(3-V[st,L[hg],F[hg]]-X[m,L[hg]]-X[m,F[hg]]) for hg in HG if L[hg] != F[hg]
                                                                                                                                for st in ST if st == 'CC'
                                                                                                                                    for m in M if m in SM[st]), name='(12)') # TODO è correto che l'heatgroup sia lo stesso per L ed F
    mdl.addConstrs((X[m,f'P{_get_product_index(p)}'] == X[m, f'P{_get_product_index(p)+1}'] for hg in HG 
                                                                                                for p in HGP[hg] if p not in L[hg] 
                                                                                                    for m in M), name='(13, non è quello del paper)')                                                                                                                               
    mdl.addConstrs((tsstage[P[i+1], st] == tfstage[P[i], st] for hg in HG for i in range(len(P)-1) if P[i] != L[hg] for st in ST if st == 'CC'), name='(14)')    
    mdl.addConstrs((V[st,p,p1] == 1 for hg in HG for p in P if p in HGP[hg] for p1 in P if _get_product_index(p) < _get_product_index(p1) and p1 in HGP[hg] for st in ST ), name='(15)') # TODO: check insiemi (devo mettere anche HG ???) (la precedenza è su prodotti di uno stesso HG, non su quelli totali)
    mdl.addConstrs((V[st,p,p1] == 0 for p in P for p1 in P if _get_product_index(p) == _get_product_index(p1) for st in ST), name='(16)')  
    
    # energy 
    mdl.addConstrs((tsstage[p,st] >= tau[S[i-1]]*ys[p,st,S[i]] for p in P for st in ST for i in range(2, len(S)+1)), name='(17)')
    mdl.addConstrs((tsstage[p,st] <= tau[s]+(HORIZON-tau[s])*(1-ys[p,st,s]) for p in P for st in ST for s in S), name='(18)')
    mdl.addConstrs((tfstage[p,st] >= tau[S[i-1]]*yf[p,st,S[i]] for p in P for st in ST for i in range(2, len(S)+1)), name='(19)')
    mdl.addConstrs((tfstage[p,st] <= tau[s] + (HORIZON-tau[s])*(1-yf[p,st,s]) for p in P for st in ST for s in S), name='(20)')

    
    # OBJECTIVE FUNCTION
    mdl.setObjective(gp.quicksum(ts[m, p] for m in M for p in P), GRB.MINIMIZE) 
    return mdl









