import urllib.request
import urllib.parse
import json
import random

def fetch_autobahn_data(all_roads=False, country_code="AT"):
    # Overpass QL query to get 'motorway' (Autobahn) in a specific country
    overpass_url = "http://overpass-api.de/api/interpreter"
    highway_filter = 'way["highway"]' if all_roads else 'way["highway"="motorway"]'
    overpass_query = f"""
    [out:json][timeout:300];
    area["ISO3166-1"="{country_code}"][admin_level=2]->.searchArea;
    (
      {highway_filter}(area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    
    # Send the HTTP request directly to OpenStreetMap's Overpass API
    data = urllib.parse.urlencode({'data': overpass_query}).encode('utf-8')
    req = urllib.request.Request(
        overpass_url, 
        data=data, 
        headers={'User-Agent': 'AutobahnMapGenerator/1.0'}
    )
    
    print("Fetching Autobahn data from OpenStreetMap Overpass API...")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def generate_drone_map(num_drones=5, output_file="autobahn.txt", all_roads=False, step_size=10000, country_code="AT", max_nodes=None):
    data = fetch_autobahn_data(all_roads=all_roads, country_code=country_code)
    
    nodes_dict = {}
    ways = []
    
    # 1. Parse nodes and ways from the OSM JSON response
    for element in data.get('elements', []):
        if element['type'] == 'node':
            nodes_dict[element['id']] = {'lat': element['lat'], 'lon': element['lon']}
        elif element['type'] == 'way':
            ways.append(element['nodes'])
            
    # Count occurrences to find intersections (nodes in multiple ways)
    node_way_counts = {}
    for way in ways:
        for n in way:
            node_way_counts[n] = node_way_counts.get(n, 0) + 1
            
    critical_nodes = set()
    for way in ways:
        if way:
            critical_nodes.add(way[0])
            critical_nodes.add(way[-1])
            for n in way:
                if node_way_counts.get(n, 0) > 1:
                    critical_nodes.add(n)
            
    # 2. Extract valid edges (connections between intersections on the autobahn)
    active_nodes = set()
    edges = set()
    
    for way in ways:
        last_critical = None
        for node in way:
            if node in nodes_dict:
                if node in critical_nodes:
                    if last_critical is not None and last_critical != node:
                        active_nodes.add(last_critical)
                        active_nodes.add(node)
                        edges.add(frozenset([last_critical, node]))
                    last_critical = node
                
    active_nodes = list(active_nodes)
    
    if not active_nodes:
        print("No autobahn data found in this region.")
        return

    # Filter out nodes if it exceeds max_nodes
    if max_nodes is not None and len(active_nodes) > max_nodes:
        active_nodes = random.sample(active_nodes, max_nodes)
        valid_nodes_set = set(active_nodes)
        
        # Filter edges to only those where BOTH ends are in the new active_nodes list
        filtered_edges = set()
        for e in edges:
            e_list = list(e)
            if e_list[0] in valid_nodes_set and (len(e_list) == 1 or e_list[1] in valid_nodes_set):
                filtered_edges.add(e)
        edges = filtered_edges

    # 3. Randomly select start and end points for the drones
    start_node = random.choice(active_nodes)
    end_node = random.choice(active_nodes)
    while start_node == end_node and len(active_nodes) > 1:
        end_node = random.choice(active_nodes)
        
    print(f"Generating custom map text file with {len(active_nodes)} hubs and {len(edges)} connections...")
    
    lines = []
    lines.append(f"nb_drones: {num_drones}")
    
    # Calculate min coordinates for offset to keep integer values reasonably small
    min_lon = min(n['lon'] for n in nodes_dict.values())
    min_lat = min(n['lat'] for n in nodes_dict.values())

    def fmt_coord(n_id):
        # Scale and offset to create integer grid coordinates
        x_int = int((nodes_dict[n_id]['lon'] - min_lon) * step_size)
        y_int = int((nodes_dict[n_id]['lat'] - min_lat) * step_size)
        return f"{x_int} {y_int}"

    def get_node_name(n_id):
        if n_id == start_node: return "hub"
        if n_id == end_node: return "goal"
        return f"hub_{n_id}"

    # Generate start and end hub definitions
    lines.append(f"start_hub: hub {fmt_coord(start_node)} [color=green]")
    lines.append(f"end_hub: goal {fmt_coord(end_node)} [color=yellow]")
    
    zones = ["normal", "restricted", "priority", "blocked"]
    colors = ["blue", "red", "green", "gray", "yellow"]

    # Generate intermediate hubs with randomized metadata
    for n_id in active_nodes:
        if n_id in (start_node, end_node):
            continue
            
        zone = random.choice(zones)
        color = random.choice(colors)
        metadata = f"[zone={zone} color={color}]"
        
        # Add max_drones logic to priority zones
        if zone == "priority" and random.random() > 0.5:
            metadata = metadata[:-1] + f" max_drones={random.randint(1, 3)}]"
            
        lines.append(f"hub: {get_node_name(n_id)} {fmt_coord(n_id)} {metadata}")
        
    # Generate undirected connections between the hubs
    for edge in edges:
        edge_list = list(edge)
        u = edge_list[0]
        # In a very rare case an edge loops on itself
        v = edge_list[1] if len(edge_list) > 1 else edge_list[0]
        
        u_name = get_node_name(u)
        v_name = get_node_name(v)
        
        connection_str = f"connection: {u_name}-{v_name}"
        
        # Add random connection capacity blocks
        if random.random() > 0.8:
            connection_str += f" [max_link_capacity={random.randint(1, 4)}]"
            
        lines.append(connection_str)
        
    # Export to text format
    with open(output_file, "w") as f:
        f.write("\n".join(lines))
        
    print(f"Map successfully saved to {output_file}.")

if __name__ == "__main__":
    generate_drone_map(
        num_drones=5, 
        output_file="autobahn_map.txt", 
        all_roads=True, 
        step_size=10000, 
        country_code="MC", 
        max_nodes=100000000
    )
