import pytest
import pandas as pd
from optimal_journey import get_stops
from sequences import find_longest_sequence  # Import from your sequence.py file

def test_simple_sequence():
    # Simple test case where all rows can be visited
    df = pd.DataFrame({
        'ID': [1, 2, 3],
        'Init_Transit': [50,50,75],
        'Edge_Transit': [50, 20, 35],
        'Expiration': [200, 250, 450]
    })
    result = find_longest_sequence(df)
    assert result == [1, 2, 3]

def test_expiration_limit():
    # Test case where the second row expires before it can be visited
    df = pd.DataFrame({
        'ID': [1, 2, 3],
        'Init_Transit': [50, 50, 50],
        'Edge_Transit': [100, 35, 35],  # Longer transit to the 2nd row
        'Expiration': [200, 100, 10]  # 2nd row expires early
    })
    result = find_longest_sequence(df)
    assert result == [1]

def test_not_first_row():
    # Test case where the second row expires before it can be visited
    df = pd.DataFrame({
        'ID': [1, 2, 3],
        'Init_Transit': [50, 50, 50],
        'Edge_Transit': [100, 35, 35],  # Longer transit to the 2nd row
        'Expiration': [20, 200, 300]  # 2nd row expires early
    })
    result = find_longest_sequence(df)
    assert result == [2, 3]

def test_multiple_sequences():
    # Test case with multiple possible sequences
    df = pd.DataFrame({
        'ID': [1, 2, 3, 4, 5],
        'Init_Transit': [50, 50, 50, 50, 50],
        'Edge_Transit': [20, 150, 100, 10, 40],  # Longer transit to row 3
        'Expiration': [200, 300, 200, 30, 400]  # Row 3 expires early
    })
    result = find_longest_sequence(df)
    assert result in [[1, 2], [4, 5]]  # Either sequence is possible

def test_empty_dataframe():
    # Test case with an empty DataFrame
    df = pd.DataFrame()
    result = find_longest_sequence(df)
    assert result == []

def get_test_get_stops_data(): # uncomment "get_" to make this a test
    # Read in CSV as DataFrame
    areas_df = pd.read_csv("areas.csv")

    # Lookup url for matching area 
    url = areas_df.loc[areas_df['area'] == 'nyc', 'url'].iloc[0]

    print(f'stop type {12} \nurl {url}')

    df2 = get_stops(12,url)

    assert len(df2) != 0 # Make sure we have some data

    df2.to_csv('test_data.csv', index=False) # Save to test_data.csv for visual inspection