import itertools
import pytest
import pandas as pd
from haversine import haversine, haversine_vector

# Assume utils and stop_analytics are modules you have available in your project
from stop_analytics import build_stop_graph


@pytest.fixture()
def stops_df():
    return pd.DataFrame(
        {
            "row_num": [0, 1, 2],
            "name": ["Stop 1", "Stop 2", "Stop 3"],
            "lat": [37.7749, 37.7849, 37.849],
            "lng": [-122.4194, -122.4294, -122.4394],
            "cool": [10, 20, 15],
        }
    )


@pytest.fixture()
def cooldown_df():
    return pd.DataFrame({"distance": [100, 200], "cooldown": [5, 10]})


def test_build_stop_graph_single_stop(
    stops_df: pd.DataFrame, cooldown_df: pd.DataFrame
):
    G = build_stop_graph(stops_df.head(1), cooldown_df)

    node_list = list(G.nodes())
    edge_list = list(G.edges())

    assert len(node_list) == 1
    assert len(edge_list) == 0
    assert G.nodes[0]["name"] == "Stop 1"
    assert G.nodes[0]["cooldown"] == 10


def test_build_stop_graph_two_stops(stops_df, cooldown_df):
    G = build_stop_graph(stops_df.head(2), cooldown_df)

    node_list = list(G.nodes())
    edge_list = list(G.edges())

    assert len(node_list) == 2
    assert len(edge_list) == 1
    assert G.nodes[0]["name"] == "Stop 1"
    assert G.nodes[0]["cooldown"] == 10
    assert G.nodes[1]["name"] == "Stop 2"
    assert G.nodes[1]["cooldown"] == 20

    # Calculate haversine distance between nodes
    lat1, lng1 = stops_df.iloc[0]["lat"], stops_df.iloc[0]["lng"]
    lat2, lng2 = stops_df.iloc[1]["lat"], stops_df.iloc[1]["lng"]
    expected_distance = haversine((lat1, lng1), (lat2, lng2))

    actual_distance = G.edges[0, 1]["distance"]
    assert pytest.approx(actual_distance) == expected_distance
    assert G.edges[0, 1]["weight"] == 5 * 60


def test_vectorized_distance(stops_df):
    coords = stops_df[["lat", "lng"]]

    dist_matrix = haversine_vector(coords, coords, comb=True)

    assert dist_matrix.shape == (3, 3)

    stops_pairs = list(itertools.combinations(stops_df.index, 2))

    for pair in stops_pairs:
        row1 = stops_df.loc[pair[0], ["lat", "lng"]]
        row2 = stops_df.loc[pair[1], ["lat", "lng"]]
        expected_distance = haversine((row1.lat, row1.lng), (row2.lat, row2.lng))
        actual_distance = dist_matrix[pair[0], pair[1]]
        assert pytest.approx(actual_distance) == expected_distance
