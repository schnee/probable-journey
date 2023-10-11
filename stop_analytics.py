import networkx as nx
from haversine import haversine, Unit
#import optimal_journey as oj
import pandas as pd
import utils
import itertools


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
    G = nx.Graph()

    for index, row in stops.iterrows():
        G.add_node(row['row_num'], name=row['name'], pos=(row['lat'], row['lng']),
               cooldown = row['cool'])

    for i, row1 in stops.iterrows():
        for j, row2 in stops.iterrows():
            if i >= j: 
                continue # avoid duplicate edges
            dist = haversine((row1['lat'], row1['lng']), 
                         (row2['lat'], row2['lng']))
            G.add_edge(i, j, distance=dist, weight=utils.cooldown(dist,df_cool))
    return G



def path_weight(G, path):
    initial_node = path[0]
    initial_cooldown = G.nodes[initial_node]['cooldown']
    # seed the total weight with the initial cooldown; this is the
    # to the first node in the path, from where the journey will begin.

    total_weight = initial_cooldown

    for j in range(len(path)-1):
        node1 = path[j]
        node2 = path[j+1]
        edge_data = G.edges[node1, node2]
        weight = edge_data['weight']
        total_weight += weight
    return total_weight


def reorder_stops(stops, df_cool):
    G = build_stop_graph(stops, df_cool)

    paths = dict(nx.all_pairs_dijkstra_path(G, weight='weight'))

    nodes = list(G.nodes)
    all_paths = []

    for start_node in nodes:
        rotated_nodes = rotate_list(nodes, nodes.index(start_node)) 
        path = min_path(paths, rotated_nodes)
        all_paths.append(path)

    lightest_path = min(all_paths, key=lambda x: path_weight(G, x))

    # lightest_path is list of node ids

    stop_order = []
    for node_id in lightest_path:
      stop_order.append(stops.loc[stops['row_num'] == node_id].index[0])

    stops = stops.loc[stop_order].reset_index(drop=True)

# Add empty column to hold edge weights
    stops['edge_cool'] = stops['cool']  

# Fill edge weights iterating through stops   
    for i in range(1, len(stops)):
      node1 = stops.loc[i-1, 'row_num']
      node2 = stops.loc[i, 'row_num']
  
      edge_data = G.edges[node1, node2]
      weight = edge_data['weight']
  
      stops.at[i, 'edge_cool'] = weight
    return stops

if __name__ == "__main__":
    stops = utils.get_stops(12)

    df_cool = utils.get_cooldown()

    stops = reorder_stops(stops, df_cool)

    print(stops)
