import numpy as np
from read_data import process_all_instances
from feasibility_checker import *
#from feasibility_checker import get_route_cost, Route, is_feasible
from helpers import get_objective

def get_route(routes, courier_id):
    # for route in routes:
    #     if route.rider_id == courier_id:
    #         return route
    # return None   
    return routes[courier_id-1]

def generate_initial_solution(couriers, deliveries):
    # Create a list of Route objects for each courier
    routes = [Route(courier.courier_id, []) for courier in couriers]

    # Sort deliveries and couriers by capacity in descending order
    sorted_deliveries = sorted(deliveries, key=lambda x: x.capacity, reverse=True)
    sorted_couriers = sorted(couriers, key=lambda x: x.capacity, reverse=True)

    too_large_deliveries = []  # List to store deliveries that are too large for any courier

    # Distribute deliveries among couriers
    for i, delivery in enumerate(sorted_deliveries):
        courier_idx = i % len(couriers)  # Distribute deliveries equally among couriers
        courier = sorted_couriers[courier_idx]  # Get the current courier
        
        # Check if the delivery fits the courier's capacity
        if delivery.capacity <= courier.capacity:
            route = get_route(routes, courier.courier_id)
            #route = routes[courier_idx]  # Get the Route object for this courier
            
            # Append the delivery pickup and drop-off to the courier's route (Route.stops)
            route.stops.append(delivery.delivery_id)   # Append pickup (positive delivery ID)
            route.stops.append(delivery.delivery_id)  # Append dropoff (negative delivery ID)
        else:
            # If the delivery is too large, add it to the too_large_deliveries list
            too_large_deliveries.append(delivery)

    # Handle too large deliveries
    for delivery in too_large_deliveries:
        assigned = False
        for courier in sorted_couriers:
            # Try to find a courier that can carry this too-large delivery (e.g., a special case)
            if courier.capacity >= delivery.capacity:
                route = get_route(routes, courier.courier_id)  # Find the route for the courier
                #route = routes[couriers.index(courier)]  # Find the route for the courier
                route.stops.append(delivery.delivery_id)  # Append pickup
                route.stops.append(delivery.delivery_id)  # Append dropoff
                assigned = True
                break

        if not assigned:
            print(f"Warning: Delivery {delivery.delivery_id} could not be assigned to any courier due to capacity limitations.")

    # Return the generated routes
    return routes


if __name__ == "__main__":
    # get all 
    training_data_folder = "training_data"
    all_instance_data = process_all_instances(training_data_folder)
    for instance_data in all_instance_data:
        
        couriers = instance_data['couriers']
        deliveries = instance_data['deliveries']
        distance_matrix = np.array(instance_data['travel_time'])

        # remove first line and first column
        distance_matrix = distance_matrix[1:, 1:]
        distance_matrix = distance_matrix.astype(int)
        initial_solution = generate_initial_solution(couriers, deliveries)
        for route in initial_solution:
            route_is_feasible = is_feasible(route,couriers,deliveries)
            if not route_is_feasible:
                print("Route is not feasible")   

        objective = get_objective(initial_solution, couriers, deliveries, distance_matrix)
        print(instance_data['instance_name'], objective)