import networkx as nx
from haversine import haversine, Unit
import pandas as pd
import utils
import itertools
# import optimal_journey as oj


def rotate_list(lst, n):
  return lst[n:] + lst[:n]

def min_path(paths, theNodes):
    path = []
    current = theNodes[0] 
    while theNodes:
        path.append(current)
        theNodes.remove(current)
        if not theNodes:
            break
        
        next_node = min(theNodes, key=lambda x: paths[current][x])
        current = next_node
    return path

def build_stop_graph(stops, df_cool):
    """
    Build a graph representing the stops and their connections.


    Parameters:
        stops (pandas.DataFrame): Dataframe containing stop information
        df_cool (pandas.DataFrame): Dataframe containing cooldown information

    Returns:
        G (networkx.Graph): The built graph
    """
    G = nx.Graph()  # initialize an empty graph

    # Add nodes with coordinates and cooldown
    for stop_row in stops.loc[:, ['row_num', 'name', 'lat', 'lng', 'cool']].itertuples(index=True):
        """
        Add a node for each stop, with its coordinates and cooldown value
        """
        G.add_node(stop_row.row_num, 
                name=stop_row.name, 
                pos=(stop_row.lat, stop_row.lng), 
                cooldown=stop_row.cool)

    # Create a fully-connected graph
    # Add edges with distances and weights
    stops_pairs = list(itertools.combinations(stops.index, 2))
    for pair in stops_pairs:
        """
        Create edges between all pairs of stops
        Calculate the distance between each pair of stops using the haversine formula
        Calculate the weight of each edge using the cooldown function
        """
        row1 = stops.loc[pair[0], ['lat', 'lng']]
        row2 = stops.loc[pair[1], ['lat', 'lng']]
        dist = haversine((row1.lat, row1.lng), (row2.lat, row2.lng))
        G.add_edge(pair[0], pair[1], 
                distance=dist, 
                weight=utils.cooldown(dist, df_cool))

    return G  # return the built graph


def path_weight(G, path):
    """
    Calculates the total weight of a path in the graph G.

    Parameters:
    G (Graph): The graph to calculate the path weight for.
    path (list): The list of node IDs that make up the path.

    Returns:
    total_weight (int): The total weight of the path.
    """

    total_weight = 0
    for node1, node2 in zip(path, path[1:]):
        total_weight += G.nodes[node1]['cooldown'] + G.edges[node1, node2]['weight']
    return total_weight

def calculate_all_shortest_paths(stop_graph):
    """Calculates shortest paths between all pairs of nodes in the graph."""
    return dict(nx.all_pairs_dijkstra_path(stop_graph, weight='weight'))

def find_path_with_minimum_cost(all_paths, stop_graph):
    """Finds the path with the minimum total weight from all_paths."""
    return min(all_paths, key=lambda path: path_weight(stop_graph, path))

def reorder_stops(pokestops, cooldown_by_distance):
    stop_graph = build_stop_graph(pokestops, cooldown_by_distance)

    paths = calculate_all_shortest_paths(stop_graph)

    nodes = list(stop_graph.nodes)
    all_paths = []

    for start_node in nodes:
        rotated_nodes = rotate_list(nodes, nodes.index(start_node)) 
        path = min_path(paths, rotated_nodes)
        all_paths.append(path)

    lightest_path = find_path_with_minimum_cost(all_paths, stop_graph)

    # lightest_path is list of node ids

    stop_order = []
    for node_id in lightest_path:
      stop_order.append(pokestops.loc[pokestops['row_num'] == node_id].index[0])

    pokestops = pokestops.loc[stop_order].reset_index(drop=True)

# Add empty column to hold edge weights
    pokestops['edge_cool'] = pokestops['cool']  

# Fill edge weights iterating through stops   
    for i in range(1, len(pokestops)):
      node1 = pokestops.loc[i-1, 'row_num']
      node2 = pokestops.loc[i, 'row_num']
  
      edge_data = stop_graph.edges[node1, node2]
      weight = edge_data['weight']
  
      pokestops.at[i, 'edge_cool'] = weight
    return pokestops

if __name__ == "__main__":

       # Read in CSV as DataFrame
    areas_df = pd.read_csv("areas.csv")

    # Lookup url for matching area 
    area = "nyc"
    url = areas_df.loc[areas_df['area'] == area, 'url'].iloc[0]


    stops = oj.get_stops(12, url)

    df_cool = utils.get_cooldown()

    stops = reorder_stops(stops, df_cool)

    print(stops)
