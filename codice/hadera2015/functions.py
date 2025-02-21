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


