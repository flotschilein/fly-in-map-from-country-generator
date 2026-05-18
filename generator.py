import osmnx as ox
import networkx as nx

def generate_drone_config(location_name, nb_drones=5):
    # 1. Download and project street network
    G = ox.graph_from_place(location_name, network_type='drive')
    G_proj = ox.project_graph(G)
    nodes, edges = ox.graph_to_gdfs(G_proj)
    
    # Dictionary to track the highest capacity connected to each node
    node_capacities = {node_id: 1 for node_id in G_proj.nodes()}
    connection_list = []
    
    # 2. Pre-process Connections to find Hub capacities
    node_ids = list(G_proj.nodes())
    start_node = node_ids[0]
    end_node = node_ids[-1]

    for u, v, k, data in G_proj.edges(keys=True, data=True):
        highway_type = data.get('highway', 'road')
        
        # Determine link capacity
        if any(h in str(highway_type) for h in ['motorway', 'trunk', 'primary']):
            cap = 10
        elif 'secondary' in str(highway_type):
            cap = 5
        else:
            cap = 2
            
        # Update the max capacity for both nodes connected by this edge
        node_capacities[u] = max(node_capacities[u], cap)
        node_capacities[v] = max(node_capacities[v], cap)
        
        # Store connection string for later
        u_name = f"hub_{u}" if u == start_node else f"node_{u}"
        v_name = f"goal_{v}" if v == end_node else f"node_{v}"
        connection_list.append(f"connection: {u_name}-{v_name} [max_link_capacity={cap}]")

    # 3. Generate Output Lines
    lines = [f"nb_drones: {nb_drones}", ""]
    
    # 4. Process Hubs (using the calculated capacities)
    lines.append("# ── HUBS ──")
    for node_id, data in nodes.iterrows():
        x, y = int(data['x'] / 10), int(data['y'] / 10)
        hub_cap = node_capacities[node_id]
        
        if node_id == start_node:
            lines.append(f"start_hub: hub_{node_id} {x} {y} [color=green max_drones={hub_cap}]")
        elif node_id == end_node:
            lines.append(f"end_hub: goal_{node_id} {x} {y} [color=yellow max_drones={hub_cap}]")
        else:
            lines.append(f"hub: node_{node_id} {x} {y} [zone=normal color=blue max_drones={hub_cap}]")
            
    # 5. Add Connections
    lines.append("")
    lines.append("# ── CONNECTIONS ──")
    lines.extend(connection_list)

    return "\n".join(lines)

# Example usage:
config_text = generate_drone_config("Saarland", nb_drones=50)
with open("Heilbronnx.txt", "w") as f:
    f.write(config_text)

print("File generated with dynamic hub capacities!")