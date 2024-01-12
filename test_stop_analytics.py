import pytest
import pandas as pd
from haversine import haversine

# Assume utils and stop_analytics are modules you have available in your project
from stop_analytics import build_stop_graph 

@pytest.fixture()
def stops_df():
    return pd.DataFrame({'row_num': [0, 1], 
                         'name': ['Stop 1', 'Stop 2'], 
                         'lat': [37.7749, 37.7849], 
                         'lng': [-122.4194, -122.4294], 
                         'cool': [10, 20]})

@pytest.fixture()
def cooldown_df():
    return pd.DataFrame({'distance': [100, 200], 
                         'cooldown': [5, 10]})


def test_build_stop_graph_single_stop(stops_df, cooldown_df):

    print(stops_df.head(1))

    G = build_stop_graph(stops_df.head(1), cooldown_df)

    node_list = list(G.nodes())
    edge_list = list(G.edges())

    assert len(node_list) == 1
    assert len(edge_list) == 0
    assert G.nodes[0]['name'] == 'Stop 1'
    assert G.nodes[0]['cooldown'] == 10


def test_build_stop_graph_two_stops(stops_df, cooldown_df):
    G = build_stop_graph(stops_df, cooldown_df)

    node_list = list(G.nodes())
    edge_list = list(G.edges())

    assert len(node_list) == 2
    assert len(edge_list) == 1
    assert G.nodes[0]['name'] == 'Stop 1'
    assert G.nodes[0]['cooldown'] == 10
    assert G.nodes[1]['name'] == 'Stop 2'
    assert G.nodes[1]['cooldown'] == 20

    # Calculate haversine distance between nodes
    lat1, lng1 = stops_df.iloc[0]['lat'], stops_df.iloc[0]['lng']
    lat2, lng2 = stops_df.iloc[1]['lat'], stops_df.iloc[1]['lng']
    expected_distance = haversine((lat1, lng1), (lat2, lng2))

    actual_distance = G.edges[0, 1]['distance']
    assert pytest.approx(actual_distance) == expected_distance
    assert G.edges[0, 1]['weight'] == 5 * 60