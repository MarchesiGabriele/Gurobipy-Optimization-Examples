import gurobipy as gp
from gurobipy import GRB
import data

def get_hedera_model() -> gp.Model:
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
    tau = data.tau


    # DECISION VARIABLES
    X = mdl.addVars(M,P, vtype=GRB.BINARY, name='product_to_machine')
    tf = mdl.addVars(M,P, vtype=GRB.CONTINUOUS, name='time_finish')
    ts = mdl.addVars(M,P, vtype=GRB.CONTINUOUS, name='time_start')
    tfstage = mdl.addVars(P,ST, vtype=GRB.CONTINUOUS, name='time_finish_stage') 
    tsstage = mdl.addVars(P,ST, vtype=GRB.CONTINUOUS, name='time_start_stage') 
    w = mdl.addVars(P,ST, vtype=GRB.CONTINUOUS, name='slack_after_stage' ) # TODO: capire se è giusto indicisìzzare su ST
    V = mdl.addVars(ST, P, P, vtype=GRB.BINARY, name='precedence')

    # !!!! POSSIBILE PROBLEMA: quando ho {st, m} in SM, potrei avere un errore, dato che io sto iterando per tutte le coppie m ed st !!!!!!!!!!!!!!!!!!
    # TODO: CHECK
    HORIZON = 24*60

    # CONSTRAINTS
    mdl.addConstrs((gp.quicksum(X[m,p] for m in SM[st]) == 1 for p in P for st in ST), name='(1)')
    mdl.addConstrs((tf[m,p] == ts[m,p] + X[m,p]*teta[p][m] for m in M for p in P), name='(2)')
    mdl.addConstrs((ts[m,p] <= HORIZON*X[m,p] for m in M for p in P), name='(3)') # TODO: M nel constraint posso mettere il tempo max di start, fine time horizon ?
    mdl.addConstrs((tsstage[p,st] == gp.quicksum(ts[m,p] for m in SM[st]) for p in P for st in ST), name='(4)')
    mdl.addConstrs((tfstage[p,st] == gp.quicksum(tf[m,p] for m in SM[st]) for p in P for st in ST), name='(5)')
    mdl.addConstrs((tsstage[p,ST[i+1]] == tfstage[p,ST[i]] + w[p,ST[i]] for p in P for i in range(len(ST)-1)), name='(6)') # Constraint linking consecutive stages
    mdl.addConstrs((tmin[m][m1]*(X[m,p]+X[m1,p]-1) <= w[p,ST[i]] for p in P 
                                                                    for i in range(len(ST)-1)
                                                                        for m in M if m in SM[ST[i]]
                                                                            for m1 in M if m1 in SM[ST[i+1]]), name='(7.1)') # TODO: CHECK
    mdl.addConstrs((w[p,st] <= tmax[p][st] for p in P 
                                                for st in ST if st != 'CC'), name='(7.2)') # TODO: CHECK
    mdl.addConstrs((V[st, p, p1] + V[st, p1, p] == 1 for st in ST for p in P for p1 in P), name='(8)')
    mdl.addConstrs((V[ST[i], p, p1] == V[ST[i+1], p, p1] for i in range(len(ST)-1) for p in P for p1 in P), name='(9)')
    mdl.addConstrs((ts[m,p1] >= tf[m,p] + tsetup[m] - (HORIZON+ tsetup[m])*(3-V[st,p,p1]-X[m,p]-X[m,p]) for p in P if p != p1
                                                                                                            for p1 in P if p != p1 
                                                                                                                for m in M 
                                                                                                                    for st in ST if st != 'CC'), name='(10)') # TODO: MOLTO PROBABILE ERRORE!
    mdl.addConstrs((ts[m,p1] >= tf[m,p] - HORIZON*(3-V[st,p,p1]-X[m,p]-X[m,p1]) for p in P if p != p1
                                                                                for p1 in P if p != p1
                                                                                    for m in M    
                                                                                        for st in ST if st == 'CC'), name='(11)')
    mdl.addConstrs((ts[m,p1] >= tf[m,p] + tsetup[m] - (HORIZON+ tsetup[m])*(3-V[st,p,p1]-X[m,p]-X[m,p1]) for hg in HG
                                                                                                        for p in L[hg] 
                                                                                                            for p1 in F[hg] if p != p1
                                                                                                                for m in M     
                                                                                                                    for st in ST if st == 'CC'), name='(12)')
    mdl.addConstrs((tmax[p1]['EAF'] == gp.max_(tmax[p]['EAF'] for p in P) 
                        + gp.max_([tau[p]['AOD1'], tau[p]['AOD2']] for p in P)
                            + gp.max_(tmax[p]['AOD'] for p in P) + gp.max_([teta[p]['LF1'], teta[p]['LF2']] for p in P)
                                + gp.max_(w[p]['LF'] for p in P) for p1 in P), name='(13)') # TODO: check funzione max + controllare TAU
    mdl.addConstrs((ts[p+1, st] == tf[p, st] for p in P if p not in L[hg] for hg in HG for st in ST if st == 'CC'), name='(14)')    
    mdl.addConstrs((V[st, p, p1] == 1 for p in P for p1 in P if p<p1 for st in ST), name='(15)') # TODO: check insiemi (devo mettere anche HG ???) (la precedenza è su prodotti di uno stesso HG, non su quelli totali)
    mdl.addConstrs((V[st,p,p1] == 0 for p in P for p1 in P if p == p1 for st in ST), name='(16)')    


    # OBJECTIVE FUNCTION
    mdl.setObjective(gp.quicksum(tf[m, p] for m in M if m == 'CC1' or m == 'CC2' for p in P), GRB.MINIMIZE) 
    return mdl











