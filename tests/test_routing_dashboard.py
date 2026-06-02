import pytest
import numpy as np
import pandas as pd
from src.data_processor import load_and_filter_data
from src.routing_engine import solve_tsp, haversine_distance, get_osrm_distance_matrix

def test_kpi_normalization_and_filtering(tmp_path):
    # Create mock CSV data to test strict filtering
    mock_data = pd.DataFrame({
        'store_id': ['STR_01', 'STR_02', 'STR_03', 'STR_04', 'STR_05', 'STR_06'],
        'name': [
            'Local Specialized Store', 
            'Petstock Franchise Ryde',  # Should be filtered out by name
            'Petbarn Warehouse',        # Should be filtered out by name
            'Ryde Special Store', 
            'Macquarie Specialized', 
            'Woolworths Supermarket'    # Should be filtered out by name
        ],
        'address': ['1 St', '2 St', '3 St', '4 St', '5 St', '6 St'],
        'suburb': ['Suburb A'] * 6,
        'chain?': ['False', 'True', 'False', 'False', 'False', 'False'],  # STR_02 filtered by column
        'website_url': ['http://url'] * 6,
        'phone_number': ['123'] * 6,
        'lat': [-33.78, -33.79, -33.80, -33.81, -33.82, -33.83],
        'lng': [151.11, 151.12, 151.13, 151.14, 151.15, 151.16],
        'apportioned_pop': [5000] * 6,
        'pop_density_per_sqkm': [100.0, 200.0, 300.0, 400.0, 500.0, 600.0],
        'distance_km': [1.0] * 6
    })
    
    csv_file = tmp_path / "test_stores.csv"
    mock_data.to_csv(csv_file, index=False)
    
    # Run data processor
    processed_df = load_and_filter_data(str(csv_file))
    
    # STR_02 (Petstock, chain?=True), STR_03 (Petbarn), STR_06 (Woolworths) should be filtered out
    # STR_01, STR_04, STR_05 should remain
    remaining_ids = processed_df['store_id'].tolist()
    assert 'STR_01' in remaining_ids
    assert 'STR_04' in remaining_ids
    assert 'STR_05' in remaining_ids
    assert 'STR_02' not in remaining_ids  # Filtered by chain?
    assert 'STR_03' not in remaining_ids  # Filtered by name
    assert 'STR_06' not in remaining_ids  # Filtered by name
    
    # KPI validation (1-10 range check)
    assert processed_df['kpi_score'].min() == 1.0
    assert processed_df['kpi_score'].max() == 10.0

def test_haversine_calculation():
    # Macquarie Park coordinates
    coord1 = (-33.7792, 151.1216)
    coord2 = (-33.7444, 151.1426)
    
    dist = haversine_distance(coord1, coord2)
    # Distance is roughly 4-5 km. Let's make sure it returns a positive int within reasonable bounds.
    assert dist > 1000
    assert dist < 10000

def test_tsp_solver():
    origin = (-33.7850, 151.1200)
    # Define 5 stores
    stores = [
        [-33.7768, 151.1212],
        [-33.7444, 151.1426],
        [-33.7912, 151.1022],
        [-33.7650, 151.1510],
        [-33.8050, 151.1300]
    ]
    
    # Solve TSP
    route, dist_matrix = solve_tsp(origin, stores)
    
    # Index 0 is origin. The length of route should be 7 (origin + 5 stores + return to origin)
    assert len(route) == 7
    assert route[0] == 0
    assert route[-1] == 0
    
    # Verify that all indices 0, 1, 2, 3, 4, 5 are visited exactly once (except 0 which is start/end)
    assert set(route) == {0, 1, 2, 3, 4, 5}
