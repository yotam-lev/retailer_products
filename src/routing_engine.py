from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def haversine_distance(coord1, coord2):
    """
    Calculate the great circle distance between two points on the earth (specified in decimal degrees)
    to serve as a reliable mathematical fallback if OSRM is offline.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    R = 6371000  # radius of Earth in meters
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    
    a = np.sin(dphi / 2.0) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0) ** 2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    
    return int(R * c)

def get_osrm_distance_matrix(coords):
    """
    Retrieve driving distances from OSRM table service. Falls back to Haversine distance matrix if offline.
    """
    num_locations = len(coords)
    try:
        # Construct OSRM request for a 6x6 matrix (lng,lat order)
        loc_str = ";".join([f"{c[1]},{c[0]}" for c in coords])
        url = f"http://router.project-osrm.org/table/v1/driving/{loc_str}?annotations=distance"
        
        response = requests.get(url, timeout=5).json()
        if response.get('code') == 'Ok' and 'distances' in response:
            return np.array(response['distances'])
    except Exception as e:
        logger.warning(f"OSRM table API failed, using Haversine distance fallback: {e}")
    
    # Fallback to straight-line distance matrix
    dist_matrix = np.zeros((num_locations, num_locations))
    for i in range(num_locations):
        for j in range(num_locations):
            dist_matrix[i][j] = haversine_distance(coords[i], coords[j])
    return dist_matrix

def solve_tsp(origin_coords, store_coords):
    """
    Solve the Traveling Salesperson Problem (TSP) using Google OR-Tools.
    Returns:
        route: List of indices in optimized traversal order (starts and ends at 0).
        distance_matrix: The distance matrix used for calculations.
    """
    coords = [origin_coords] + store_coords
    num_locations = len(coords)
    
    # Get distance matrix
    dist_matrix = get_osrm_distance_matrix(coords)
    
    # OR-Tools Solver setup
    manager = pywrapcp.RoutingIndexManager(num_locations, 1, 0)
    routing = pywrapcp.RoutingModel(manager)
    
    def distance_callback(from_index, to_index):
        # Convert routing variable index to distance matrix node index
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(dist_matrix[from_node][to_node])
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    
    solution = routing.SolveWithParameters(search_parameters)
    
    if not solution:
        # Fallback to simple direct order if no solution is found
        logger.warning("OR-Tools failed to find a TSP solution. Returning sequential order.")
        return list(range(num_locations)) + [0], dist_matrix
    
    index = routing.Start(0)
    route = []
    while not routing.IsEnd(index):
        route.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    route.append(manager.IndexToNode(index))
    
    return route, dist_matrix

def get_osrm_route_geometry(coords):
    """
    Query OSRM route service to fetch the actual road-network geometry.
    Coordinates must be a list of (lat, lng) in journey order.
    Returns:
        polyline_coords: List of (lat, lng) mapping the exact road path.
        total_distance: Total driving distance in meters.
        total_duration: Total driving duration in seconds.
    """
    try:
        loc_str = ";".join([f"{c[1]},{c[0]}" for c in coords])
        url = f"http://router.project-osrm.org/route/v1/driving/{loc_str}?overview=full&geometries=geojson"
        
        response = requests.get(url, timeout=5).json()
        if response.get('code') == 'Ok' and 'routes' in response and len(response['routes']) > 0:
            route = response['routes'][0]
            geojson_coords = route['geometry']['coordinates']
            # Convert GeoJSON [lng, lat] back to Folium [lat, lng]
            polyline_coords = [[pt[1], pt[0]] for pt in geojson_coords]
            return polyline_coords, route['distance'], route['duration']
    except Exception as e:
        logger.warning(f"OSRM route API failed, using straight-line geometry fallback: {e}")
        
    # Fallback: simple straight-line connection between target stops
    # Calculate a rough distance/duration based on Haversine distance
    total_dist = 0
    for i in range(len(coords) - 1):
        total_dist += haversine_distance(coords[i], coords[i+1])
    # Assume 40 km/h (11.1 m/s) average city driving speed for duration calculation
    total_dur = total_dist / 11.1
    return coords, total_dist, total_dur

