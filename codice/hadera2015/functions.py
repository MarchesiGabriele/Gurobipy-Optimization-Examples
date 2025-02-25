import gurobipy as gp
import model  # Import the model module to access data structures

def draw_gantt_chart(gurobi_model: gp.Model):
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Get unique products (heats)
    products = model.data.heat
    
    # Create a color map for products
    colors = plt.cm.get_cmap('tab20')(np.linspace(0, 1, len(products)))
    color_dict = dict(zip(products, colors))
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Collect all y-axis labels (machines and stages)
    y_labels = []
    y_pos = []
    current_pos = 0
    
    # Add machines
    for m in model.data.equipment:
        y_labels.append(f"Machine {m}")
        y_pos.append(current_pos)
        
        # Plot bars for each product on this machine
        for p in products:
            try:
                start_time = gurobi_model.getVarByName(f'time_start[{m},{p}]').X
                finish_time = gurobi_model.getVarByName(f'time_finish[{m},{p}]').X
                 
                if abs(start_time) > 0 or abs(finish_time) > 0:
                    ax.barh(current_pos, 
                            finish_time - start_time,
                            left=start_time,
                            color=color_dict[p],
                            alpha=0.7,
                            label=f'Product {p}' if current_pos == 0 else "")
                    
                    # Add text label in the middle of the bar
                    ax.text(start_time + (finish_time - start_time)/2,
                            current_pos,
                            f'P{p}',
                            ha='center',
                            va='center')
            except:
                continue
        
        current_pos += 1
    
    # Add stages
    for st in model.data.production_stage:
        y_labels.append(f"Stage {st}")
        y_pos.append(current_pos)
        
        # Plot bars for each product in this stage
        product_count = 0  # Counter to alternate text position
        for p in products:
            try:
                start_time = gurobi_model.getVarByName(f'time_start_stage[{p},{st}]').X
                finish_time = gurobi_model.getVarByName(f'time_finish_stage[{p},{st}]').X
                
                if abs(start_time) > 0 or abs(finish_time) > 0:
                    ax.barh(current_pos,
                           finish_time - start_time,
                           left=start_time,
                           color=color_dict[p],
                           alpha=0.3)
                    
                    # Add text label in the middle of the bar, alternating between two vertical positions
                    vertical_offset = 0.2 if product_count % 2 == 0 else -0.2
                    ax.text(start_time + (finish_time - start_time)/2,
                           current_pos + vertical_offset,
                           f'P{p}',
                           ha='center',
                           va='center')
                    product_count += 1
            except:
                continue
        
        current_pos += 1
    
    # Customize the plot
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel('Time')
    ax.set_title('Production Schedule Gantt Chart')
    ax.grid(True, axis='x', alpha=0.3)
    
    # Add legend
    handles = [plt.Rectangle((0,0),1,1, color=color_dict[p]) for p in products]
    ax.legend(handles, [f'Product {p}' for p in products], 
             loc='upper right',
             bbox_to_anchor=(1.15, 1))
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Show the plot
    plt.show()

def print_time_variables(gurobi_model: gp.Model):
    from data import time_interval, heat, production_stage, tau
    
    times = [int(t) for t in time_interval]
    
    print("\n=== Time Variables Analysis ===")
    for t in times:
        print(f"\nTime slot {t}:")
        print(f"tau[{t}] = {tau[str(t)]}")  # Print tau value for this time slot
        print("-" * 50)
        
        # For each product and stage
        for p in heat:
            for st in production_stage:
                # Get start and finish times
                ts_stage = gurobi_model.getVarByName(f'time_start_stage[{p},{st}]').X
                tf_stage = gurobi_model.getVarByName(f'time_finish_stage[{p},{st}]').X
                
                # Get corresponding ys and yf values
                ys = gurobi_model.getVarByName(f'product_to_time_interval_start[{p},{st},{t}]').X
                yf = gurobi_model.getVarByName(f'product_to_time_interval_finish[{p},{st},{t}]').X
                
                # Print only if any of these values is non-zero
                if abs(ts_stage) > 1e-6 or abs(tf_stage) > 1e-6 or abs(ys) > 1e-6 or abs(yf) > 1e-6:
                    # print(f"Product {p}, Stage {st}:")
                    # print(f"  ts = {ts_stage:.2f}, ys = {ys}")
                    # print(f"  tf = {tf_stage:.2f}, yf = {yf}")
                    pass

def print_all_flows(gurobi_model: gp.Model):
    from data import time_interval, arc, node
    
    print("\n=== Flow Values Analysis ===")
    
    # Get all variables from the model
    all_vars = gurobi_model.getVars()
    
    # Filter flow variables and organize them by time slot
    flow_vars = {}
    for var in all_vars:
        if var.VarName.startswith('flow on arch on time s'):
            # Try to parse the variable name to get time slot and nodes
            try:
                # Remove 'flow on arch on time s[' from start and ']' from end
                indices = var.VarName.replace('flow on arch on time s[', '').replace(']', '')
                t, source, dest = indices.split(',')
                
                # Store in dictionary
                if t not in flow_vars:
                    flow_vars[t] = []
                flow_vars[t].append((source, dest, var.X))
            except Exception as e:
                print(f"Error parsing variable {var.VarName}: {str(e)}")
    
    # Print organized results
    print("\n=== Organized Flow Results ===")
    # Sort time slots numerically
    for t in sorted(flow_vars.keys(), key=int):
        print(f"\nTime slot {t}:")
        print("-" * 50)
        
        # Group flows by source node for better organization
        flows_by_source = {}
        for source, dest, value in flow_vars[t]:
            if source not in flows_by_source:
                flows_by_source[source] = []
            flows_by_source[source].append((dest, value))
        
        # Print flows organized by source node
        for source in sorted(flows_by_source.keys(), key=int):
            for dest, value in sorted(flows_by_source[source], key=lambda x: int(x[0])):
                if abs(value) > 1e-6:  # Only print non-zero flows
                    print(f"Flow ({source}->{dest}): {value:.2f}")
        print("\n")

def plot_energy_prices(gurobi_model: gp.Model = None):
    import matplotlib.pyplot as plt
    import numpy as np
    from data import costi_energia_3, time_interval
    
    # Create figure and axis with two y-axes
    fig, ax1 = plt.subplots(figsize=(15, 6))
    ax2 = ax1.twinx()  # Create a second y-axis sharing the same x-axis
    
    # Prepare data for plotting
    times = [int(t) for t in time_interval]
    
    # Extract prices for supplier 3
    prices_purchase = costi_energia_3
    
    # Plot prices on the first y-axis
    lines1 = []
    lines1.append(ax1.plot(times, prices_purchase, 'r-', label='Purchase Price', linewidth=2)[0])
    
    # Plot energy consumption on the second y-axis if model is provided
    lines2 = []
    if gurobi_model is not None:
        # Get energy consumption (q) values
        q_consumption = []
        for t in times:
            try:
                q_var = gurobi_model.getVarByName(f'energy used in time slot[{t}]')
                if q_var is not None:
                    q_consumption.append(q_var.X)
                else:
                    print(f"Variable 'energy used in time slot[{t}]' not found")
                    q_consumption.append(0)
            except:
                q_consumption.append(0)
        
        # Plot q on the second y-axis
        lines2.append(ax2.plot(times, q_consumption, 'k--', label='Energy Used (q)', 
                              linewidth=3, alpha=0.7)[0])
        
        # Print debug info
        print("\nEnergy consumption values (q):", q_consumption)
    
    # Customize the first y-axis (prices)
    ax1.set_xlabel('Time Interval')
    ax1.set_ylabel('Price')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(times)
    
    # Customize the second y-axis (energy consumption)
    if gurobi_model is not None:
        ax2.set_ylabel('Energy Consumption')
    
    # Add legend combining both axes
    all_lines = lines1 + lines2
    all_labels = [line.get_label() for line in all_lines]
    ax1.legend(all_lines, all_labels, 
              loc='lower right',  # Position the legend in the lower right
              bbox_to_anchor=(0.98, 0.02))  # Fine-tune the position
    
    plt.title('Energy Price and Consumption Over Time')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Show the plot
    plt.show()

def plot_flows(gurobi_model: gp.Model):
    import matplotlib.pyplot as plt
    import numpy as np
    from data import time_interval, arc, node
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(15, 6))
    
    # Prepare data for plotting
    times = [int(t) for t in time_interval]
    
    # Initialize flow data structures
    flows = {
        'purchase1': [],  # Flow 1->5
        'purchase2': [],  # Flow 2->5
        'purchase3': [],  # Flow 3->5
        'generation': [], # Flow 4->5
        'sold': [],      # Flow 5->6
        'used': []       # Flow 5->7
    }
    
    # Collect flow data
    for t in time_interval:
        # Purchase flows
        flows['purchase1'].append(gurobi_model.getVarByName(f'flow on arch on time s[{t},1,5]').X)
        flows['purchase2'].append(gurobi_model.getVarByName(f'flow on arch on time s[{t},2,5]').X)
        flows['purchase3'].append(gurobi_model.getVarByName(f'flow on arch on time s[{t},3,5]').X)
        flows['generation'].append(gurobi_model.getVarByName(f'flow on arch on time s[{t},4,5]').X)
        flows['sold'].append(gurobi_model.getVarByName(f'flow on arch on time s[{t},5,6]').X)
        flows['used'].append(gurobi_model.getVarByName(f'flow on arch on time s[{t},5,7]').X)
    
    # Plot flows
    ax.plot(times, flows['purchase1'], 'b-', label='Purchase Type 1 (1->5)', linewidth=2)
    ax.plot(times, flows['purchase2'], 'g-', label='Purchase Type 2 (2->5)', linewidth=2)
    ax.plot(times, flows['purchase3'], 'r-', label='Purchase Type 3 (3->5)', linewidth=2)
    ax.plot(times, flows['generation'], 'y-', label='Generation (4->5)', linewidth=2)
    ax.plot(times, flows['sold'], 'm--', label='Energy Sold (5->6)', linewidth=3)
    ax.plot(times, flows['used'], 'k--', label='Energy Used (5->7)', linewidth=3)
    
    # Customize the plot
    ax.set_xlabel('Time Interval')
    ax.set_ylabel('Energy Flow')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(times)
    
    # Add legend
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.title('Energy Flows Over Time')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Show the plot
    plt.show()
    
    # Print the values for verification
    print("\n=== Energy Flow Values ===")
    for t in times:
        print(f"\nTime slot {t}:")
        print(f"Purchase Type 1: {flows['purchase1'][t-1]:.2f}")
        print(f"Purchase Type 2: {flows['purchase2'][t-1]:.2f}")
        print(f"Purchase Type 3: {flows['purchase3'][t-1]:.2f}")
        print(f"Generation: {flows['generation'][t-1]:.2f}")
        print(f"Energy Sold: {flows['sold'][t-1]:.2f}")
        print(f"Energy Used: {flows['used'][t-1]:.2f}")
        print("-" * 30)


