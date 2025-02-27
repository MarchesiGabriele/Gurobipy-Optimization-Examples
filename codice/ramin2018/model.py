import gurobipy as gp
from gurobipy import GRB
import data


# Energy market (prendo energia necessaria per soddisfare la domanda)
# Reserve market (gestisco eventuali opportunità aggiuntive)


def get_optimal_power_profiles_simplified(casting_line: str) -> gp.Model:
    mdl = gp.Model("Energy Market Simple")

    # 4 furnaces, 2 power lines (2 furnaces each), 1 castin line

    # SETS
    F = data.furnaces
    M = data.jobs
    MF = data.M
    J = data.stages
    C = data.casting_lines
    L = data.power_lines
    JE = data.energy_based_stages
    JT = data.time_based_stages
    FL = data.FL
    FC = data.FC
    K = data.time_grid

    # PARAMETERS
    rcast = 210 # [m3/s]
    vpour = 1400 # [m3] 
    #vtap = 1400/1  # only one tap # TODO: GIOCARE CON QUESTO VALORE
    # vcast = 1400 #?? # TODO: GIOCARE CON QUESTO VALORE
    E_hat = data.E_hat # energy for each stage
    Pmax = 1000000 # [MW] # TODO SECONDO ME DEVE ESSERE DI PIU DATO CHE E' LA POTENZA TOTALE E NON SOLO QUELLA DI UNA MACCHINA
    Plmax = 16 # [MW]
    PstageMin = data.pminstage
    PstageMax = data.pmaxstage
    deltat = 5 # [min]
    delta_hat = data.stage_time
    buffer_level_start = 0 # TODO GIOCARE CON QUESTO VALORE
    vtl = 1400 # TODO: GIOCARE CON QUESTO VALORE
    lambdada = data.prezzi_orari


    # VARIABLES
    p = mdl.addVars(K,F,M,J, vtype=GRB.CONTINUOUS, name='power')
    t = mdl.addVars(F,M,J, vtype=GRB.CONTINUOUS, name='stage_starting_times')
    x = mdl.addVars(K,F,M,J, vtype=GRB.BINARY, name='stage_activation')
    y = mdl.addVars(K,F,M,J, vtype=GRB.BINARY, name='supplementary_features')
    costo_cl = mdl.addVars(C, vtype=GRB.CONTINUOUS, name='costo_casting_line')
    vtap = mdl.addVars(K,F, vtype=GRB.CONTINUOUS, name='casting_volume')
    buffer_level = mdl.addVars(K, vtype=GRB.CONTINUOUS, name='buffer_level')


    HORIZON = 24*60*60


    # CONSTRAINTS
    mdl.addConstrs((gp.quicksum(p[k,f,m,j]*deltat*60 for k in K) == E_hat[f][m][j] for f in F for m in MF[f] for j in JE), name='(4)')
    mdl.addConstrs((t[f,m,JT[i+1]] - t[f,m,JT[i]] >= delta_hat[f][m][JT[i]] for f in F for m in MF[f] for i in range(len(JT)-1)), name='(5)')
    # tempo tra ultimo stage di un job e primo stage del job successivo
    mdl.addConstrs((t[f,MF[f][i+1],'LOADING'] - t[f,MF[f][i],J[len(J)-1]] >= delta_hat[f][MF[f][i+1]]['LOADING'] for f in F for i in range(len(MF[f])-1)), name='(6)')
    mdl.addConstrs(((1-x[k,f,m,j])*(1+int(k))<= t[f,m,j]/deltat for f in F for m in MF[f] for k in K for j in J), name='(7.1)')
    mdl.addConstrs((t[f,m,j]/deltat <= x[k,f,m,j]*HORIZON + (1-x[k,f,m,j])*HORIZON for f in F for m in MF[f] for k in K for j in J), name='(7.2)') 
    mdl.addConstrs((PstageMin[f][m][J[i]]*(x[k,f,m,J[i]] - x[k,f,m,J[i+1]]) <= p[k,f,m,J[i]] for f in F for m in MF[f] for k in K for i in range(len(J)-1)), name='(8.1)')
    mdl.addConstrs((p[k,f,m,J[i]] <= PstageMax[f][m][J[i]]*(x[k,f,m,J[i]] - x[k,f,m,J[i+1]]) for f in F for m in MF[f] for k in K for i in range(len(J)-1)), name='(8.2)')
    mdl.addConstrs((gp.quicksum(gp.quicksum(gp.quicksum(p[k,f,m,j] for j in J) for m in MF[f]) for f in FL[l]) <= Plmax for l in L for k in K), name='(9)')
    mdl.addConstrs((gp.quicksum(gp.quicksum(gp.quicksum(p[k,f,m,j] for j in J) for m in MF[f]) for f in F) <= Pmax for k in K), name='(10)')
    mdl.addConstrs((PstageMin[f][m][j]*y[k,f,m,j] <= p[k,f,m,j] for f in F for m in MF[f] for k in K for j in J), name='(11.1)') 
    mdl.addConstrs((p[k,f,m,j] <= PstageMax[f][m][j]*y[k,f,m,j] for f in F for m in MF[f] for k in K for j in J), name='(11.2)') 
    mdl.addConstrs((buffer_level[k] == buffer_level_start + gp.quicksum(vtap[k,f] for f in FC[c]) - rcast*deltat for c in C for k in K), name='(14)')
    mdl.addConstrs((vtap[k,f] == vtl * gp.quicksum(x[k,f,m,'TAPPING'] for m in MF[f]) for f in F for k in K), name='(16)') 
    mdl.addConstr((costo_cl[casting_line] == gp.quicksum(gp.quicksum(gp.quicksum(gp.quicksum(p[k,f,m,j]*lambdada[k]*deltat for k in K) for j in J) for m in MF[f]) for f in FC[casting_line] for c in C)), name='(20)')


    # OBJECTIVE
    mdl.setObjective(costo_cl[casting_line], GRB.MINIMIZE)
    return mdl




def get_optimal_power_profiles(casting_line: str) -> gp.Model:
    mdl = gp.Model("Energy Market")

    # SETS
    C = data.casting_lines
    F = data.melting_furnaces
    L = data.power_lines
    K = data.time_grid
    M = data.melt_jobs   # TODO: CHECK
    J = data.stages
    JE = data.energy_based_stages
    JT = data.time_based_stages
    Jtp = data.tapping_stages
    FL = data.power_line_furnaces  
    FC = data.casting_line_furnaces

    # 8 fornaci per il melting stage


    # PARAMETERS
    E = data.actual_stage_energy
    E_hat =  data.min_stage_energy
    E_hat_sp = data.min_energy_splash
    alpha = None # TODO: ADD 
    delta_hat = None # TODO: ADD
    deltat = 5 # min 
    delta_hat_of = None # TODO
    delta_fc = data.ladle_travel_time # TODO
    Kmin = data.kmin # TODO
    Kmax = data.kmax # TODO
    Pmin_stage = data.pmin_stage # TODO
    Pmax_stage = data.pmax_stage # TODO
    Pmax_line = data.pmax_line # TODO
    Pmax = data.pmax # TODO
    Pzero = data.initial_power # TODO
    rpwr = data.power_rate_limit # TODO
    rof = data.overflow_rate_limit # TODO
    rsp = data.splash_rate_limit # TODO
    rcast = data.casting_rate # TODO
    vcmin = data.buffer_lower_limit # TODO
    vczero = data.starting_buffer_volume # TODO
    vcmax =  data.buffer_upper_limit # TODO
    vtap = data.tapping_volume # TODO
    vtl = data.ladle_volume# TODO
    vcast = data.casting_volume # TODO
    N = data.num_of_intervals_rates
    kcn = data.breakpoint_cast
    gamma = data.power_volume_holding_furnaces # TODO
    Lmax = data.max_numer_of_ladles # TODO
    lambdada = data.lambda_casting_line # TODO

    # VARIABLES
    p = mdl.addVars(K,F,M,J, vtype=GRB.CONTINUOUS, name='power')
    ptilde = mdl.addVars(K,C, vtype=GRB.CONTINUOUS, name='total_power_holding_furnaces')
    t = mdl.addVars(F,M,J, vtype=GRB.CONTINUOUS, name='stage_starting_times')
    x = mdl.addVars(K,F,M,J, vtype=GRB.BINARY, name='stage_activation')
    y = mdl.addVars(K,F,M,J, vtype=GRB.BINARY, name='supplementary_features')
    costo_cl = mdl.addVars(C, vtype=GRB.CONTINUOUS, name='costo_casting_line')

    # CONSTRAINTS
    # (1) ??
    # (2) ??
    # TODO: FIXARE capire se j1 fa parte di JE o di J, capire come inserire j2 (inoltre se ho i-1 capire se devo inziare dallo step successivo)
    mdl.addConstrs((E[f][m][JE[i]] == E_hat[f][m][JE[i]]*(1 + gp.quicksum(alpha[f][m][J[i1]]*(t[f,m,J[i1+1]]-t[f,m,J[i1]])/delta_hat[f][m][J[i1]] 
                                                                    for i1 in range(len(JE)) if i1 <= i and i1 > i-1)) 
                                                                        for f in F for m in MF[f] for i in range(len(JE))), name='(3)')
    mdl.addConstrs((gp.quicksum(p[k,f,m,j]*deltat for k in K) == E[f][m][j] for f in F for m in MF[f] for j in JE), name='(4)')
    mdl.addConstrs((t[f,m,JT[i+1]] - t[f,m,JT[i]] >= delta_hat[f][m][JT[i]] for f in F for m in MF[f] for i in range(len(JT)-1)), name='(5)')
    mdl.addConstrs((t[f,MF[f][i+1],1] - t[f,MF[f][i],J[len(J)]] >= delta_hat[f][MF[f][i+1]][1] for f in F for i in range(len(MF[f])-1)), name='(6)')
    mdl.addConstrs(((1-x[k,f,m,j])*(1+k) + Kmin[f][m][j] <= t[f,m,j]/deltat for f in F for m in MF[f] for k in K for j in J), name='(7.1)')
    mdl.addConstrs((t[f,m,j]/deltat <= x[k,f,m,j] + (1-x[k,f,m,j])*Kmax[f][m][j] for f in F for m in MF[f] for k in K for j in J), name='(7.2)')
    mdl.addConstrs((Pmin_stage[f][m][J[i]]*(x[k,f,m,J[i]] - x[k,f,m,J[i+1]]) <= p[k,f,m,J[i]] for f in F for m in MF[f] for k in K for i in range(len(J)-1)), name='(8.1)')
    mdl.addConstrs((p[k,f,m,J[i]] <= Pmax_stage[f][m][J[i]]*(x[k,f,m,J[i]] - x[k,f,m,J[i+1]]) for f in F for m in MF[f] for k in K for i in range(len(J)-1)), name='(8.2)')
    mdl.addConstrs((gp.quicksum(gp.quicksum(gp.quicksum(p[k,f,m,j] for j in J) for m in MF[f]) for f in FL[l]) <= Pmax_line[l] for l in L for k in K), name='(9)')
    mdl.addConstrs((gp.quicksum(gp.quicksum(gp.quicksum(p[k,f,m,j] for j in J) for m in MF[f]) for f in F) <= Pmax for k in K), name='(10)')
    mdl.addConstrs((Pmin_stage[f][m][j]*y[k,f,m,j] <= p[k,f,m,j] for f in F for m in MF[f] for k in K for j in J), name='(11.1)') # TODO: Controllare che pmin e pmax siano giusti con questi indici, controllare anche l'indice J
    mdl.addConstrs((p[k,f,m,j] <= Pmax_stage[f][m][j]*y[k,f,m,j] for f in F for m in MF[f] for k in K for j in J), name='(11.2)') # TODO: Controllare che pmin e pmax siano giusti con questi indici, controllare anche l'indice J
    mdl.addConstrs((p[K[i],f,m,J[1]] <= Pzero + rpwr*gp.quicksum(y[K[i1],f,m,J[1]]*deltat for i1 in range(i)) for f in F for m in MF[f] for i in range(len(K))), name='(12)')
    mdl.addConstrs((rof*(gp.quicksum(x[K[i1],f,m,J[2]]*deltat for i1 in range(i)) - delta_hat_of) <= gp.quicksum(p[K[i1],f,m,J[2]]*deltat for i1 in range(i)) for f in F for m in MF[f] for i in range(len(K))), name='(13.1)')
    mdl.addConstrs((gp.quicksum(p[K[i1],f,m,J[2]]*deltat for i1 in range(i)) <= E_hat_sp + rsp*gp.quicksum(x[K[i1],f,m,J[2]]*deltat for i1 in range(i)) for f in F for m in MF[f] for i in range(len(K))), name='(13.2)')
    mdl.addConstrs((vcmin[c] <= vczero[c] + gp.quicksum(vtap[K[i-delta_fc[f][c]],f]) - vcast[K[i]][c] for c in C for f in FC[c] for i in range(len(K))), name='(14.1)') # TODO capire se devo iterare per c 
    mdl.addConstrs((vczero[c] + gp.quicksum(vtap[K[i-delta_fc[f][c]],f]) - vcast[K[i]][c] <= vcmax[c] for c in C for f in FC[c] for i in range(len(K))), name='(14.2)') # TODO capire se devo iterare per c 
    mdl.addConstrs((vcast[k][c] == gp.quicksum((kcn[c][N[i1]]*(rcast[c][N[i1+1]]-rcast[c][N[i1]]) - rcast[c][N[i+1]]*k)*deltat for i1 in range(1, len(N[c])-1)) for c in C for i in range(1, len(N[c])-1) for k in K), name='(15)') # TODO: Controllare se N[i] è giusto
    mdl.addConstrs((vtap[k][f][m] == vtl * gp.quicksum(gp.quicksum(x[k,f,m,j] for j in Jtp) for m in MF[f]) for f in F for m in MF[f] for k in K), name='(16)') # TODO controllare index
    mdl.addConstrs((ptilde[k,c] == gamma[c]*(vczero[c] + gp.quicksum(gp.quicksum(vtap[k][f][m] - vcast[k][c] for m in MF[f]) for f in FC)) for c in C for k in K), name='(17)')
    # mdl.addConstrs((gp.quicksum(gp.quicksum(gp.quicksum(gp.quicksum(x[K[i],f,m,j] - x[K[i-delta_fc[f][c]],f,m,j] for j in Jtp) for m in MF[f]) for f in FC[c]) for c in C) <= Lmax for i in range(len(K))), name='(19)')
    mdl.addConstrs((costo_cl[casting_line] == gp.quicksum(gp.quicksum(gp.quicksum(gp.quicksum(p[k,f,m,j]*lambdada[k]*deltat for k in K) for j in J) for m in MF[f]) for f in FC[casting_line] for c in C) + gp.quicksum(ptilde[k,casting_line]*lambdada[k]*deltat for k in K)), name='(20)')
    # OBJECTIVE
    mdl.setObjective(costo_cl[casting_line], GRB.MINIMIZE)



