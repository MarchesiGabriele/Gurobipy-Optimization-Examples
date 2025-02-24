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
    NODE = data.node
    PUR = data.pur
    DEM = data.dem
    GEN = data.gen
    BAL = data.bal
    SALE = data.sale
    ARC = data.arc
    aload = None # TODO: AGGIUNGERE


    # PARAMETERS
    teta = data.teta
    tmin = data.tmin
    tmax = data.tmax
    tsetup = data.tsetup
    tau = data.tau
    HORIZON = 24*60
    MAX_FLOW = 40
    fmin = data.flowmin
    fmax = data.flowmax
    cstart = 1000
    k = 0.2
    rmin = 3 # hours 
    dmin = 3 # hours
    po = 100 
    pu = 80 
    c_weight = 1


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
    ysaux = mdl.addVars(P,M,ST,S, vtype=GRB.CONTINUOUS, name='aux var start')   
    yfaux = mdl.addVars(P,M,ST,S, vtype=GRB.CONTINUOUS, name='aux var finish')   
    a = mdl.addVars(P,M,ST,S, vtype=GRB.CONTINUOUS, name='task start-end within time slot')  # a,b,c,d indicano i 4 casi del contributo di consumo energia in ciascuno slot
    b = mdl.addVars(P,M,ST,S, vtype=GRB.CONTINUOUS, name='task start before and finish within time slot')
    c = mdl.addVars(P,M,ST,S, vtype=GRB.CONTINUOUS, name='task start within and finish after time slot')
    d = mdl.addVars(P,M,ST,S, vtype=GRB.CONTINUOUS, name='task start before and finish after time slot')
    q = mdl.addVars(S, vtype=GRB.CONTINUOUS, name='energy used in time slot')
    h = mdl.addVars(P,M, vtype=GRB.CONTINUOUS, name='power consumption')
    f = mdl.addVars(S,NODE,NODE, vtype=GRB.CONTINUOUS, name='flow on arch on time s')
    G = mdl.addVars(S,NODE,NODE, vtype=GRB.BINARY, name='plant is active')
    gs = mdl.addVars(S,NODE,NODE, vtype=GRB.BINARY, name='generator startup')
    cgen = mdl.addVars(S, vtype=GRB.CONTINUOUS, name='on site gen cost')
    muh = mdl.addVars(vtype=GRB.CONTINUOUS, name='total cost energy')
    bo = mdl.addVars(S, vtype=GRB.CONTINUOUS, name='upper bound')
    bu = mdl.addVars(S, vtype=GRB.CONTINUOUS, name='lower bound')
    co = mdl.addVars(S, vtype=GRB.CONTINUOUS, name='over consumption')
    cu = mdl.addVars(S, vtype=GRB.CONTINUOUS, name='lower consumption')
    delta = mdl.addVar(vtype=GRB.CONTINUOUS, name='deviation penalty')

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
    mdl.addConstrs((tsstage[p,st] >= tau[S[i-1]]*ys[p,st,S[i]] for p in P for st in ST for i in range(2, len(S)+1)), name='(17)') # TODO: CHECK time (controllare S, tau e come viene indicizzato in questo vincolo)
    mdl.addConstrs((tsstage[p,st] <= tau[s]+(HORIZON-tau[s])*(1-ys[p,st,s]) for p in P for st in ST for s in S), name='(18)')
    mdl.addConstrs((tfstage[p,st] >= tau[S[i-1]]*yf[p,st,S[i]] for p in P for st in ST for i in range(2, len(S)+1)), name='(19)') # TODO: check time
    mdl.addConstrs((tfstage[p,st] <= tau[s] + (HORIZON-tau[s])*(1-yf[p,st,s]) for p in P for st in ST for s in S), name='(20)')
    mdl.addConstrs((ysaux[p,m,st,s] >= X[m,p] + ys[p,st,s] - 1 for p in P for st in ST for m in M if M in SM[st] for s in S), name='(21)')
    mdl.addConstrs((ysaux[p,m,st,s] <= X[m,p] for p in P for st in ST for m in M if m in SM[st] for s in S), name='(22)')
    mdl.addConstrs((ysaux[p,m,st,s] <= ys[p,st,s] for p in P for st in ST for m in M if m in SM[st] for s in S), name='(23)')
    mdl.addConstrs((yfaux[p,m,st,s] >= X[m,p] + yf[p,st,s] - 1 for p in P for st in ST for m in M if m in SM[st] for s in S), name='(24)')
    mdl.addConstrs((yfaux[p,m,st,s] <= X[m,p] for p in P for st in ST for m in M if m in SM[st] for s in S), name='(25)')
    mdl.addConstrs((yfaux[p,m,st,s] <= yf[p,st,s] for p in P for st in ST for m in M if m in SM[st] for s in S), name='(26)')
    mdl.addConstrs((a[p,m,st,s] >= ysaux[p,m,st,s] + yfaux[p,m,st,s] - 1 for p in P for st in ST for m in M if m in SM[st] for s in S), name='(27)')
    mdl.addConstrs((a[p,m,st,s] <= ysaux[p,m,st,s] for p in P for st in ST for m in M if m in SM[st] for s in S), name='(28)')
    mdl.addConstrs((a[p,m,st,s] <= yfaux[p,m,st,s] for p in P for st in ST for m in M if m in SM[st] for s in S), name='(29)')
    mdl.addConstrs((b[p,m,st,S[i]] >= tf[p,m] - tau[S[i-1]] - (HORIZON - tau[S[i-1]])*(1-yfaux[p,m,st,S[i]]+ysaux[p,m,st,S[i]]) for p in P     
                                                                                                                                for st in ST 
                                                                                                                                    for m in M if m in SM[st] 
                                                                                                                                        for i in range(2, len(S)+1)), name='(30)')
    mdl.addConstrs((b[p,m,st,S[i]] <= tf[p,m] - tau[S[i-1]] + tau[S[i-1]]*(1-yfaux[p,m,st,S[i]]) for p in P for st in ST for m in M if m in SM[st] for i in range(2, len(S)+1)), name='(31)')
    mdl.addConstrs((b[p,m,st,S[i]] <= (tau[S[i]]-tau[S[i-1]])*yfaux[p,m,st,S[i]] for p in P for st in ST for m in M if m in SM[st] for i in range(2, len(S)+1)), name='(32)') 
    mdl.addConstrs((b[p,m,st,S[i]] <= (tau[S[i]] - tau[S[i-1]])*(1-ysaux[p,m,st,S[i]]) for p in P for st in ST for m in M if m in SM[st] for i in range(2, len(S)+1)), name='(33)')
    mdl.addConstrs((c[p,m,st,s] >= tau[s] - ts[p,m] - tau[s]*(1-ysaux[p,m,st,s]+yfaux[p,m,st,s]) for p in P for st in ST for m in M if m in SM[st] for s in S), name='(34)')
    mdl.addConstrs((c[p,m,st,s] <= tau[s] - ts[p,m] + (HORIZON - tau[s])*(1-ysaux[p,m,st,s]) for p in P for st in ST for m in M if m in SM[st] for s in S), name='(35)') 
    mdl.addConstrs((c[p,m,st,S[i]] <= (tau[S[i]] - tau[S[i-1]])*ysaux(p,m,st,S[i]) for p in P for st in ST for m in M if m in SM[st] for i in range(2, len(S)+1)), name='(36)')
    mdl.addConstrs((c[p,m,st,S[i]] <= (tau[S[i]]-tau[S[i-1]])*(1-yfaux[p,m,st,S[i]]) for p in P for st in ST for m in M if m in SM[st] for i in range(2, len(S)+1)), name='(37)')
    mdl.addConstrs((d[p,m,st,S[i]] >= (tau[S[i]]-tau[S[i-1]])
                                            *(gp.quicksum(ysaux[p,m,st,s1] for s1 in S if int(s1) < int(S[i]))+gp.quicksum(yfaux[p,m,st,s1] for s1 in S if int(s1) > int(S[i]))-1)
                                                 for p in P for st in ST for m in M if m in SM[st] for i in range(2, len(S)+1)), name='(38)')
    mdl.addConstrs((d[p,m,st,S[i]] <= (tau[S[i]] - tau[S[i-1]])*gp.quicksum(ysaux[p,m,st,s1] for s1 in S if int(s1) < int(S[i])) 
                                                                                    for p in P for st in ST for m in M if m in SM[st] for i in range(2, len(S)+1)), name='(39)')
    mdl.addConstrs((d[p,m,st,S[i]] <= (tau[S[i]]-tau[S[i-1]])*gp.quicksum(yfaux[p,m,st,s1] for s1 in S if int(s1) > int(S[i]))
                                                                                    for p in P for st in ST for m in M if m in SM[st] for i in range(2, len(S)+1)), name='(40)')
    mdl.addConstrs((d[p,m,st,S[i]] <= (tau[S[i]]-tau[S[i-1]])*(1-ysaux[p,m,st,S[i]]) for p in P for st in ST for m in M if m in SM[st] for i in range(2, len(S)+1)), name='(41)')
    mdl.addConstrs((d[p,m,st,S[i]] <= (tau[S[i]]-tau[S[i-1]])*(1-yfaux[p,m,st,S[i]]) for p in P for st in ST for m in M if m in SM[st] for i in range(2, len(S)+1)), name='(42)')
    mdl.addConstrs((q[s] == gp.quicksum(h[p,m]*(a[p,m,st,s]*teta[p,m]+b[p,m,st,s]+c[p,m,st,s+d[p,m,st,s]]) for p in P for st in ST for m in M if m in SM[st])/60 for s in S), name='(43)') # TODO: è giusto usare TETA al posto di TAU ??
    mdl.addConstrs((gp.quicksum(ys[p,st,s] for s in S) == gp.quicksum(X[m,p] for m in M if m in SM[st]) for p in P for st in ST), name='(44)')
    mdl.addConstrs((gp.quicksum(yf[p,st,s] for s in S) == gp.quicksum(X[m,p] for m in M if m in SM[st]) for p in P for st in ST), name='(45)')
    mdl.addConstrs((gp.quicksum(X[m,p]*h[p,m]*teta[p,m] for p in P for m in M if m in SM[st] for st in ST)/60 == gp.quicksum(q[s] for s in S)), name='(46)') # TODO: devo usare TETA al posto di PI ? oppure a+b+c+d ?
    # grafo
    mdl.addConstrs((gp.quicksum(f[s,i,j1] for i in NODE if j1 in ARC[i]) == gp.quicksum(f[s,j1,j] for j in NODE if j in ARC[j1]) for j1 in BAL for s in S ), name='(47)')
    mdl.addConstrs((fmin[s][i][j] <= f[s,i,j] for s in S for i in NODE for j in NODE if j in ARC[i]), name='(48.1)')
    mdl.addConstrs((f[s,i,j] <= fmax[s][i][j] for s in S for i in NODE for j in NODE if j in ARC[i]), name='(48.2)')
    mdl.addConstrs((q[s] == gp.quicksum(f[s,i,j] for i in NODE for j in DEM if j in ARC[i]) for s in S), name='(49)')
    mdl.addConstrs((G[s,i,j] <= f[s,i,j] for i in GEN for j in BAL if j in ARC[i] for s in S), name='(50.1)')
    mdl.addConstrs((f[s,i,j] <= MAX_FLOW*G[s,i,j] for i in GEN for j in BAL if j in ARC[i] for s in S), name='(50.2)')
    mdl.addConstrs((G[S[i1],i,j] - G[S[i1-1],i,j] <= gs[S[i1],i,j] for i in GEN for j in BAL if j in ARC[i] for i1 in range(2,len(S)+1)), name='(51.1)')
    mdl.addConstrs((gs[s,i,j] <= G[s,i,j] for i in GEN for j in BAL if j in ARC[i] for s in S), name='(51.2)') 
    mdl.addConstrs((0 <= gs[s,i,j] for i in GEN for j in BAL if j in ARC[i] for s in S), name='(52.1)')
    mdl.addConstrs((gs[S[i1],i,j] <= 1-G[S[i1-1],i,j] for i in GEN for j in BAL if j in ARC[i] for i1 in range(2,len(S)+1)), name='(52.2)')
    mdl.addConstrs((cgen[s] == gp.quicksum(f[s,i,j]*c[s,i,j] + cstart*gs[s,i,j] for i in NODE for j in GEN if j in ARC[i]) for s in S), name='(53)')
    mdl.addConstrs((f[s,i,j] == fmax[s][i][j]*G[s,i,j] - k*fmax[s][i][j]*gs[s,i,j] for i in GEN for j in BAL if j in ARC[i] for s in S), name='(54)')
    mdl.addConstrs((gp.quicksum(G[S[ii],i,j] for ii in range(i, i+rmin+1)) >= rmin*(G[S[i],i,j]-G[S[i-1],i,j]) for i in GEN for j in BAL if j in ARC[i]
                                                                                                for i in range(2, len(S)-rmin+1)), name='(55)') # TODO: check indici 
    mdl.addConstrs((gp.quicksum(G[S[ii],i,j] for ii in range(i, i+dmin+1)) <= dmin*(1+G[S[i],i,j]-G[S[i-1],i,j]) for i in GEN for j in BAL if j in ARC[i] 
                                                                                                for i in range(2, len(S)-dmin+1)), name='(56)')
    mdl.addConstrs((muh == gp.quicksum(gp.quicksum(f[s,i,j]*c[s][i][j]+cgen[s] for i in NODE for j in PUR if j in ARC[i]) 
                                        - gp.quicksum(f[s,i,j]*c[s][i][j] for i in NODE for j in SALE if j in ARC[i]) for s in S)), name='(57)')
    mdl.addConstrs((-aload[s]*bu[s] <= b[s] for s in S), name='(58.1)')
    mdl.addConstrs((b[s] <= aload[s]*bo[s] for s in S), name='(58.2)')
    mdl.addConstrs((q[s] == aload[s] + co[s] - cu[s] + b[s] for s in S), name='(59)')
    mdl.addConstrs((delta == po*gp.quicksum(co[s] for s in S) + pu*gp.quicksum(cu[s] for s in S)), name='(60)')

    # OBJECTIVE FUNCTION
    mdl.setObjective(muh + delta + c_weight*gp.quicksum(ts[m, p] for m in M for p in P), GRB.MINIMIZE) 
    return mdl










