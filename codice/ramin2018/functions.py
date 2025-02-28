def print_power_details_for_timestep(model, k_target):
    """
    Stampa il dettaglio della potenza per un dato timestep k,
    mostrando il contributo di ogni fornace, job e stage
    """
    # Recupero tutte le variabili di potenza dal modello per il timestep k
    power_vars = {var.VarName: var.X for var in model.getVars() 
                 if var.VarName.startswith(f'power[{k_target},') and var.X > 0}
    
    total_power = 0
    print(f"\nDettaglio potenze per timestep {k_target}:")
    print("-" * 50)
    
    # Organizzo i dati per fornace
    for f in ['F1', 'F2', 'F3', 'F4']:
        furnace_power = 0
        print(f"\nFornace {f}:")
        
        for m in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']:
            for j in ['LOADING', 'PRIMARY_HEATING', 'CHARGE_MELTING', 'MELTING', 
                     'ANALYSIS', 'OVERHEATING', 'TAPPING']:
                var_name = f'power[{k_target},{f},{m},{j}]'
                if var_name in power_vars:
                    power = power_vars[var_name]
                    if power > 0:  # Mostro solo i valori positivi
                        print(f"  Job {m}, Stage {j}: {power:.2f} MW")
                        furnace_power += power
        
        if furnace_power > 0:
            print(f"Totale Fornace {f}: {furnace_power:.2f} MW")
            total_power += furnace_power
    
    print("\n" + "=" * 50)
    print(f"Potenza Totale al timestep {k_target}: {total_power:.2f} MW")
    print("=" * 50)

def plot_total_power(model):
    """
    Crea un grafico della potenza totale utilizzata nel tempo, del livello del buffer,
    e del prezzo dell'elettricità, sommando la potenza di tutte le fornaci, task e stage.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from data import prezzi_orari
    
    # Recupero tutte le variabili di potenza e buffer dal modello
    power_vars = {var.VarName: var.X for var in model.getVars() if var.VarName.startswith('power')}
    buffer_vars = {var.VarName: var.X for var in model.getVars() if var.VarName.startswith('buffer_level')}
    
    # Inizializzo array per i valori
    power_values = np.zeros(288)  # 24*60/5 = 288 timesteps
    buffer_values = np.zeros(288)
    price_values = np.array([prezzi_orari[k] for k in range(288)])
    
    # Calcolo la potenza totale per ogni timestep
    for var_name, value in power_vars.items():
        k = int(var_name.split(',')[0].split('[')[1])
        power_values[k] += value
    
    # Raccolgo i valori del buffer
    for var_name, value in buffer_vars.items():
        k = int(var_name.split('[')[1].split(']')[0])
        buffer_values[k] = value
    
    # Converto potenza in kW per maggiore leggibilità
    power_values = power_values / 1e3
    
    # Creo il grafico con tre assi y
    fig, ax1 = plt.subplots(figsize=(15, 8))
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()
    
    # Sposto il terzo asse a destra del secondo
    ax3.spines['right'].set_position(('outward', 60))
    
    # Plot potenza (asse sinistro)
    line1 = ax1.plot(range(288), power_values, 'b-', linewidth=2, label='Total Power')
    ax1.fill_between(range(288), power_values, alpha=0.2, color='blue')
    
    # Plot buffer level (secondo asse)
    line2 = ax2.plot(range(288), buffer_values, 'r-', linewidth=2, label='Buffer Level', alpha=0.7)
    
    # Plot prezzo elettricità (terzo asse)
    line3 = ax3.plot(range(288), price_values, 'g-', linewidth=2, label='Electricity Price', alpha=0.7)
    
    # Calcolo e mostro statistiche della potenza
    max_power = np.max(power_values)
    
    # Aggiungo linee per massimo e media della potenza
    line4 = ax1.axhline(y=max_power, color='darkblue', linestyle='--', alpha=0.5, label=f'Max Power: {max_power:.1f} kW')
    
    # Configurazione assi
    ax1.set_xlabel('Time (hours)')
    ax1.set_ylabel('Total Power (kW)', color='b')
    ax2.set_ylabel('Buffer Level (m³)', color='r')
    ax3.set_ylabel('Electricity Price (€/kWh)', color='g')
    
    # Colore dei tick degli assi
    ax1.tick_params(axis='y', labelcolor='b')
    ax2.tick_params(axis='y', labelcolor='r')
    ax3.tick_params(axis='y', labelcolor='g')
    
    # Titolo
    plt.title('Power Consumption, Buffer Level and Electricity Price Over Time')
    
    # Aggiungo etichette per le ore sulla x
    hour_ticks = range(0, 288, 12)  # 12 intervalli di 5 minuti = 1 ora
    hour_labels = [f'{i//12}:00' for i in range(0, 288, 12)]
    ax1.set_xticks(hour_ticks)
    ax1.set_xticklabels(hour_labels, rotation=45)
    
    # Aggiungo la griglia
    ax1.grid(True, alpha=0.3)
    
    # Combino le legende dei tre assi
    lines = line1 + line2 + line3 + [line4]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper right')
    
    plt.tight_layout()
    plt.show()
    
    return power_values, buffer_values  # Ritorno i valori per eventuali analisi successive

def plot_gantt_schedule(model):
    """
    Crea un diagramma che mostra i tempi di inizio di LOADING, ANALYSIS e TAPPING
    per ogni task su ogni fornace.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Recupero i tempi di LOADING, ANALYSIS e TAPPING
    t_vars = {var.VarName: var.X for var in model.getVars() 
             if var.VarName.startswith('stage_starting_times') 
             and ('LOADING' in var.VarName or 'ANALYSIS' in var.VarName or 'TAPPING' in var.VarName)}
    
    # Dizionari per memorizzare i tempi
    loading_times = {}   # (f, m) -> start_time
    analysis_times = {}  # (f, m) -> analysis_time
    tapping_times = {}   # (f, m) -> end_time
    
    # Per ogni fornace e job, trova i tempi
    for f in ['F1', 'F2', 'F3', 'F4']:
        for m in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']:
            loading_name = f'stage_starting_times[{f},{m},LOADING]'
            analysis_name = f'stage_starting_times[{f},{m},ANALYSIS]'
            tapping_name = f'stage_starting_times[{f},{m},TAPPING]'
            
            if loading_name in t_vars:
                loading_times[(f, m)] = t_vars[loading_name]
            if analysis_name in t_vars and t_vars[analysis_name] > 0:
                analysis_times[(f, m)] = t_vars[analysis_name]
            if tapping_name in t_vars and t_vars[tapping_name] > 0:
                tapping_times[(f, m)] = t_vars[tapping_name]
    
    if not loading_times and not analysis_times and not tapping_times:
        print("No times found!")
        return
    
    # Preparo il grafico
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Colori diversi per ogni task
    colors = plt.cm.Set3(np.linspace(0, 1, 7))  # 7 colori diversi per le 7 task
    
    # Organizzo i dati per fornace
    furnace_tasks = {}
    for f in ['F1', 'F2', 'F3', 'F4']:
        furnace_tasks[f] = []
        for m in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']:
            if (f, m) in loading_times or (f, m) in analysis_times or (f, m) in tapping_times:
                furnace_tasks[f].append(m)
    
    # Trovo i limiti temporali per il grafico
    all_times = []
    for times_dict in [loading_times, analysis_times, tapping_times]:
        all_times.extend([time/3600 for time in times_dict.values()])
    min_time = max(0, min(all_times) - 1)  # Un'ora di margine
    max_time = min(24, max(all_times) + 1)  # Un'ora di margine
    
    y_ticks = []
    y_labels = []
    tasks_plotted = set()
    
    # Disegno i punti per ogni fornace
    idx = 0
    for f in ['F1', 'F2', 'F3', 'F4']:
        if furnace_tasks[f]:  # Se la fornace ha dei task
            y_ticks.append(idx)
            y_labels.append(f'Furnace {f}')
            
            for m in furnace_tasks[f]:
                color = colors[int(m[1])-1]
                
                # Disegno punto di LOADING se esiste
                if (f, m) in loading_times:
                    start_hour = loading_times[(f, m)] / 3600
                    ax.plot(start_hour, idx, 'o', markersize=10, color=color,
                           label=f'Task {m}' if m not in tasks_plotted else "")
                    tasks_plotted.add(m)
                
                # Disegno punto di ANALYSIS se esiste
                if (f, m) in analysis_times:
                    analysis_hour = analysis_times[(f, m)] / 3600
                    ax.plot(analysis_hour, idx, '^', markersize=10, color=color)
                
                # Disegno punto di TAPPING se esiste
                if (f, m) in tapping_times:
                    end_hour = tapping_times[(f, m)] / 3600
                    ax.plot(end_hour, idx, 's', markersize=10, color=color)
                    
                    # Se ho sia loading che tapping, disegno una linea tra i due
                    if (f, m) in loading_times:
                        ax.plot([start_hour, end_hour], [idx, idx], '-', color=color, alpha=0.3)
            
            idx += 1
    
    # Configurazione del grafico
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel('Time (hours)')
    ax.set_title('Loading (○), Analysis (△), and Tapping (□) Times per Task')
    
    # Imposto i limiti dell'asse x usando i valori calcolati
    ax.set_xlim(min_time, max_time)
    
    # Aggiungo la griglia
    ax.grid(True)
    ax.set_xticks(range(int(min_time), int(max_time) + 1))
    
    # Aggiungo la legenda
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.show()

def print_all_variables_for_timestep(model, k_target):
    """
    Stampa tutte le variabili decisionali per un dato timestep k
    """
    # Recupero tutte le variabili dal modello
    vars_dict = {var.VarName: var.X for var in model.getVars()}
    
    print(f"\nVariabili al timestep {k_target}:")
    print("=" * 80)
    
    # Stampo le variabili di potenza (p)
    print("\nPOTENZA (p):")
    print("-" * 40)
    for f in ['F1', 'F2', 'F3', 'F4']:
        for m in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']:
            for j in ['LOADING', 'PRIMARY_HEATING', 'CHARGE_MELTING', 'MELTING', 
                     'ANALYSIS', 'OVERHEATING', 'TAPPING']:
                var_name = f'power[{k_target},{f},{m},{j}]'
                if var_name in vars_dict and vars_dict[var_name] > 0:
                    print(f"{var_name}: {vars_dict[var_name]:.2f}")
    
    # Stampo le variabili di attivazione stage (x)
    print("\nATTIVAZIONE STAGE (x):")
    print("-" * 40)
    for f in ['F1', 'F2', 'F3', 'F4']:
        for m in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']:
            for j in ['LOADING', 'PRIMARY_HEATING', 'CHARGE_MELTING', 'MELTING', 
                     'ANALYSIS', 'OVERHEATING', 'TAPPING']:
                var_name = f'stage_activation[{k_target},{f},{m},{j}]'
                if var_name in vars_dict and vars_dict[var_name] > 0:
                    print(f"{var_name}: {int(vars_dict[var_name])}")
    
    # Stampo le variabili supplementary features (y)
    print("\nSUPPLEMENTARY FEATURES (y):")
    print("-" * 40)
    for f in ['F1', 'F2', 'F3', 'F4']:
        for m in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']:
            for j in ['LOADING', 'PRIMARY_HEATING', 'CHARGE_MELTING', 'MELTING', 
                     'ANALYSIS', 'OVERHEATING', 'TAPPING']:
                var_name = f'supplementary_features[{k_target},{f},{m},{j}]'
                if var_name in vars_dict and vars_dict[var_name] > 0:
                    print(f"{var_name}: {int(vars_dict[var_name])}")
    
    # Stampo le variabili di volume (vtap)
    print("\nVOLUME TAPPING (vtap):")
    print("-" * 40)
    for f in ['F1', 'F2', 'F3', 'F4']:
        var_name = f'tapping_volume[{k_target},{f}]'
        if var_name in vars_dict and vars_dict[var_name] > 0:
            print(f"{var_name}: {vars_dict[var_name]:.2f}")
    
    # Stampo il livello del buffer
    print("\nBUFFER LEVEL:")
    print("-" * 40)
    var_name = f'buffer_level[{k_target}]'
    if var_name in vars_dict:
        print(f"{var_name}: {vars_dict[var_name]:.2f}")
    
    print("\n" + "=" * 80)

def print_stage_info(model):
    """
    Stampa i tempi di inizio degli stage per i primi 50 timestep
    """
    # Recupero tutte le variabili dal modello
    t_vars = {var.VarName: var.X for var in model.getVars() 
             if var.VarName.startswith('stage_starting_times') 
             and ('LOADING' in var.VarName or 'TAPPING' in var.VarName or 'ANALYSIS' in var.VarName)}   
    print(t_vars)

def plot_power_per_furnace(model):
    """
    Crea quattro grafici in colonna, uno per ogni fornace,
    mostrando la potenza utilizzata nel tempo per ciascuna fornace.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from data import prezzi_orari
    
    # Recupero tutte le variabili di potenza dal modello
    power_vars = {var.VarName: var.X for var in model.getVars() if var.VarName.startswith('power')}
    
    # Inizializzo array per i valori di potenza per ogni fornace
    power_values = {
        'F1': np.zeros(288),
        'F2': np.zeros(288),
        'F3': np.zeros(288),
        'F4': np.zeros(288)
    }
    
    # Calcolo la potenza totale per ogni timestep e fornace
    for var_name, value in power_vars.items():
        parts = var_name.split(',')
        k = int(parts[0].split('[')[1])
        furnace = parts[1]
        power_values[furnace][k] += value
    
    # Converto potenza in kW per maggiore leggibilità
    for f in power_values:
        power_values[f] = power_values[f] / 1e3
    
    # Preparo i prezzi dell'elettricità
    price_values = np.array([prezzi_orari[k] for k in range(288)])
    
    # Creo il grafico con 4 subplot in colonna
    fig, axes = plt.subplots(4, 1, figsize=(15, 20))
    fig.suptitle('Power Consumption per Furnace Over Time', fontsize=16, y=0.95)
    
    # Per ogni fornace, creo un subplot
    for idx, (furnace, power) in enumerate(power_values.items()):
        ax1 = axes[idx]
        ax2 = ax1.twinx()
        
        # Plot potenza (asse sinistro)
        line1 = ax1.plot(range(288), power, 'b-', linewidth=2, label='Power')
        ax1.fill_between(range(288), power, alpha=0.2, color='blue')
        
        # Plot prezzo elettricità (asse destro)
        line2 = ax2.plot(range(288), price_values, 'g-', linewidth=2, label='Electricity Price', alpha=0.7)
        
        # Calcolo e mostro il massimo della potenza
        max_power = np.max(power)
        line3 = ax1.axhline(y=max_power, color='darkblue', linestyle='--', alpha=0.5, 
                           label=f'Max Power: {max_power:.1f} kW')
        
        # Configurazione assi
        ax1.set_ylabel('Power (kW)', color='b')
        ax2.set_ylabel('Electricity Price (€/kWh)', color='g')
        
        # Colore dei tick degli assi
        ax1.tick_params(axis='y', labelcolor='b')
        ax2.tick_params(axis='y', labelcolor='g')
        
        # Titolo del subplot
        ax1.set_title(f'Furnace {furnace}')
        
        # Etichette per le ore sulla x
        if idx == 3:  # Solo per l'ultimo subplot
            hour_ticks = range(0, 288, 12)  # 12 intervalli di 5 minuti = 1 ora
            hour_labels = [f'{i//12}:00' for i in range(0, 288, 12)]
            ax1.set_xticks(hour_ticks)
            ax1.set_xticklabels(hour_labels, rotation=45)
            ax1.set_xlabel('Time (hours)')
        else:
            ax1.set_xticks([])
        
        # Aggiungo la griglia
        ax1.grid(True, alpha=0.3)
        
        # Combino le legende
        lines = line1 + line2 + [line3]
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper right')
    
    plt.tight_layout()
    plt.show()
    
    return power_values  # Ritorno i valori per eventuali analisi successive
