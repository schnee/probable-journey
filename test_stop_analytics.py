import unittest
import pandas as pd
import networkx as nx
from haversine import haversine
from utils import cooldown
from stop_analytics import build_stop_graph

class TestBuildStopGraph(unittest.TestCase):

    def test_build_stop_graph_single_stop(self):
        stops = pd.DataFrame({'row_num': [0], 'name': ['Stop 1'], 'lat': [37.7749], 'lng': [-122.4194], 'cool': [10]})
        df_cool = pd.DataFrame({'distance': [100], 'cooldown': [5]})
        G = build_stop_graph(stops, df_cool)

        node_list = list(G.nodes())
        edge_list = list(G.edges())
        
        self.assertEqual(len(node_list), 1)
        self.assertEqual(len(edge_list), 0)
        self.assertEqual(G.nodes()[0]['name'], 'Stop 1')
        self.assertEqual(G.nodes()[0]['cooldown'], 10)

    def test_build_stop_graph_two_stops(self):
        stops = pd.DataFrame({'row_num': [0, 1], 'name': ['Stop 1', 'Stop 2'], 'lat': [37.7749, 37.7849], 'lng': [-122.4194, -122.4294], 'cool': [10, 20]})
        df_cool = pd.DataFrame({'distance': [100, 200], 'cooldown': [5, 10]})
        G = build_stop_graph(stops, df_cool)

        node_list = list(G.nodes())
        edge_list = list(G.edges())

        self.assertEqual(len(node_list), 2)
        self.assertEqual(len(edge_list), 1)
        self.assertEqual(G.nodes()[0]['name'], 'Stop 1')
        self.assertEqual(G.nodes()[0]['cooldown'], 10)
        self.assertEqual(G.nodes()[1]['name'], 'Stop 2')
        self.assertEqual(G.nodes()[1]['cooldown'], 20)

        # Calculate haversine distance between nodes
        lat1, lng1 = stops.iloc[0]['lat'], stops.iloc[0]['lng']
        lat2, lng2 = stops.iloc[1]['lat'], stops.iloc[1]['lng']
        distance = haversine((lat1, lng1), (lat2, lng2))


        self.assertAlmostEqual(G.edges[0,1]['distance'], distance, places=4)
        self.assertEqual(G.edges[0,1]['weight'], 5*60)



if __name__ == '__main__':
    unittest.main()