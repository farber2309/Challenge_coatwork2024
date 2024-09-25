import numpy as np
from read_data import process_all_instances
from feasibility_checker import *
#from feasibility_checker import get_route_cost, Route, is_feasible
from helpers import get_objective, get_route_duration, copy_route

def get_route(routes, courier_id):
    # for route in routes:
    #     if route.rider_id == courier_id:
    #         return route
    # return None   
    return routes[courier_id-1]

# def generate_initial_solution(couriers, deliveries):
#     # Create a list of Route objects for each courier
#     routes = [Route(courier.courier_id, []) for courier in couriers]

#     # Sort deliveries and couriers by capacity in descending order
#     sorted_deliveries = sorted(deliveries, key=lambda x: x.capacity, reverse=True)
#     sorted_couriers = sorted(couriers, key=lambda x: x.capacity, reverse=True)

#     too_large_deliveries = []  # List to store deliveries that are too large for any courier

#     # Distribute deliveries among couriers
#     for i, delivery in enumerate(sorted_deliveries):
#         courier_idx = i % len(couriers)  # Distribute deliveries equally among couriers
#         courier = sorted_couriers[courier_idx]  # Get the current courier
        
#         # Check if the delivery fits the courier's capacity
#         if delivery.capacity <= courier.capacity:
#             route = get_route(routes, courier.courier_id)
#             duration = get_route_duration(route, couriers, deliveries, distance_matrix)
#             #route = routes[courier_idx]  # Get the Route object for this courier
            
#             # Append the delivery pickup and drop-off to the courier's route (Route.stops)
#             route.stops.append(delivery.delivery_id)   # Append pickup (positive delivery ID)
#             route.stops.append(delivery.delivery_id)  # Append dropoff (negative delivery ID)
#         else:
#             # If the delivery is too large, add it to the too_large_deliveries list
#             too_large_deliveries.append(delivery)

#     # Handle too large deliveries
#     for delivery in too_large_deliveries:
#         assigned = False
#         for courier in sorted_couriers:
#             # Try to find a courier that can carry this too-large delivery (e.g., a special case)
#             if courier.capacity >= delivery.capacity:
#                 route = get_route(routes, courier.courier_id)  # Find the route for the courier
#                 #route = routes[couriers.index(courier)]  # Find the route for the courier
#                 route.stops.append(delivery.delivery_id)  # Append pickup
#                 route.stops.append(delivery.delivery_id)  # Append dropoff
#                 assigned = True
#                 break

#         if not assigned:
#             print(f"Warning: Delivery {delivery.delivery_id} could not be assigned to any courier due to capacity limitations.")

#     # Return the generated routes
#     return routes

# def generate_initial_solution(couriers, deliveries, distance_matrix):
#     # Create a list of Route objects for each courier
#     routes = [Route(courier.courier_id, []) for courier in couriers]

#     # Sort deliveries and couriers by capacity in descending order
#     sorted_deliveries = sorted(deliveries, key=lambda x: x.capacity, reverse=True)
#     sorted_couriers = sorted(couriers, key=lambda x: x.capacity, reverse=True)

#     too_large_deliveries = []  # List to store deliveries that are too large for any courier

#     # Distribute deliveries among couriers
#     for delivery in sorted_deliveries:
#         assigned = False
#         for courier in sorted_couriers:
#             route = get_route(routes, courier.courier_id)  # Get the Route object for this courier
            
#             # Check if the delivery fits the courier's capacity
#             if delivery.capacity <= courier.capacity:
#                 # Check if adding this delivery would exceed the max stops (4 deliveries => 8 stops)
#                 if len(route.stops) + 2 > 8:
#                     continue  # Skip to the next courier if the route is full

#                 # Check if adding this delivery would exceed the max duration (180 minutes)
#                 current_duration = get_route_duration(route, couriers, deliveries, distance_matrix)
#                 new_route = copy_route(route)
#                 new_route.stops.append(delivery.delivery_id)  # Append pickup (positive delivery ID)
#                 new_route.stops.append(delivery.delivery_id)  # Append dropoff (negative delivery ID)

#                 new_duration = get_route_duration(new_route, couriers, deliveries, distance_matrix)
                
#                 if new_duration <= 180:
#                     # Append the delivery pickup and drop-off to the courier's route
#                     route.stops.append(delivery.delivery_id)  # Append pickup (positive delivery ID)
#                     route.stops.append(delivery.delivery_id)  # Append dropoff (negative delivery ID)
#                     assigned = True
#                     break  # Delivery has been assigned, move to the next one
        
#         if not assigned:
#             # If the delivery is too large or cannot fit in any courier's route due to constraints
#             too_large_deliveries.append(delivery)

#     # Handle too-large deliveries (special cases)
#     for delivery in too_large_deliveries:
#         assigned = False
#         for courier in sorted_couriers:
#             route = get_route(routes, courier.courier_id)  # Find the route for the courier
            
#             # Try to find a courier that can carry this too-large delivery (e.g., a special case)
#             if courier.capacity >= delivery.capacity and len(route.stops) + 2 <= 8:
#                 current_duration = get_route_duration(route, couriers, deliveries, distance_matrix)
#                 new_route = copy_route(route)
#                 new_route.stops.append(delivery.delivery_id)
#                 new_route.stops.append(delivery.delivery_id)
#                 new_duration = get_route_duration(new_route, couriers, deliveries, distance_matrix)


#                 if new_duration <= 180:
#                     route.stops.append(delivery.delivery_id)  # Append pickup
#                     route.stops.append(delivery.delivery_id)  # Append dropoff
#                     assigned = True
#                     break

#         if not assigned:
#             print(f"Warning: Delivery {delivery.delivery_id} could not be assigned to any courier due to capacity, time, or stop limitations.")

#     # Return the generated routes
#     return routes

def generate_initial_solution(couriers, deliveries, distance_matrix):
    # Create a list of Route objects for each courier
    routes = [Route(courier.courier_id, []) for courier in couriers]

    # Sort deliveries and couriers by capacity in descending order
    sorted_deliveries = sorted(deliveries, key=lambda x: x.capacity, reverse=True)
    sorted_couriers = sorted(couriers, key=lambda x: x.capacity, reverse=True)

    unassigned_deliveries = []  # List to store deliveries that couldn't be assigned in the first pass

    # Distribute deliveries among couriers
    for delivery in sorted_deliveries:
        assigned = False
        for courier in sorted_couriers:
            route = get_route(routes, courier.courier_id)  # Get the Route object for this courier
            
            # Check if the delivery fits the courier's capacity
            if delivery.capacity <= courier.capacity:
                # Check if adding this delivery would exceed the max stops (4 deliveries => 8 stops)
                if len(route.stops) + 2 > 8:
                    continue  # Skip to the next courier if the route is full

                # Check if adding this delivery would exceed the max duration (180 minutes)
                current_duration = get_route_duration(route, couriers, deliveries, distance_matrix)
                new_route = copy_route(route)
                new_route.stops.append(delivery.delivery_id)  # Append pickup (positive delivery ID)
                new_route.stops.append(delivery.delivery_id)  # Append dropoff (negative delivery ID)

                new_duration = get_route_duration(new_route, couriers, deliveries, distance_matrix)
                
                if new_duration <= 180:
                    # Append the delivery pickup and drop-off to the courier's route
                    route.stops.append(delivery.delivery_id)  # Append pickup (positive delivery ID)
                    route.stops.append(delivery.delivery_id)  # Append dropoff (negative delivery ID)
                    assigned = True
                    break  # Delivery has been assigned, move to the next one
        
        if not assigned:
            # If the delivery couldn't be assigned, add it to the unassigned list
            unassigned_deliveries.append(delivery)

    # Second pass: Try to assign unassigned deliveries by prioritizing couriers with the least route duration
    for delivery in unassigned_deliveries:
        assigned = False

        # Sort couriers by their current route duration in ascending order (shortest time first)
        sorted_couriers_by_duration = sorted(sorted_couriers, key=lambda courier: get_route_duration(get_route(routes, courier.courier_id), couriers, deliveries, distance_matrix))

        for courier in sorted_couriers_by_duration:
            route = get_route(routes, courier.courier_id)  # Get the Route object for this courier
            
            # Check if the courier has enough capacity and available stops
            if delivery.capacity <= courier.capacity and len(route.stops) + 2 <= 8:
                # Check if adding this delivery would exceed the max duration (180 minutes)
                current_duration = get_route_duration(route, couriers, deliveries, distance_matrix)
                new_route = copy_route(route)
                new_route.stops.append(delivery.delivery_id)  # Append pickup
                new_route.stops.append(delivery.delivery_id)  # Append dropoff

                new_duration = get_route_duration(new_route, couriers, deliveries, distance_matrix)

                if new_duration <= 180:
                    # Assign the delivery if the route duration allows
                    route.stops.append(delivery.delivery_id)  # Append pickup
                    route.stops.append(delivery.delivery_id)  # Append dropoff
                    assigned = True
                    break  # Delivery has been assigned

        if not assigned:
            # If the delivery could not be assigned after both passes, raise an error or handle it accordingly
            print(f"Warning: Delivery {delivery.delivery_id} could not be assigned due to capacity, time, or stop limitations.")

    # Return the generated routes
    return routes




if __name__ == "__main__":
    # get all 
    training_data_folder = "training_data"
    all_instance_data = process_all_instances(training_data_folder)
    for instance_data in all_instance_data:
        print("Instance name: ", instance_data['instance_name'])
        couriers = instance_data['couriers']
        deliveries = instance_data['deliveries']
        distance_matrix = np.array(instance_data['travel_time'])

        # remove first line and first column
        distance_matrix = distance_matrix[1:, 1:]
        distance_matrix = distance_matrix.astype(int)
        initial_solution = generate_initial_solution(couriers, deliveries, distance_matrix)
        for route in initial_solution:
            # length_route = len(route.stops)
            # if length_route >0:
            #     print(route.stops)
            #     dur = get_route_duration(route, couriers, deliveries, distance_matrix)
                
            #     print("Route duration: ", dur)
            #     print("Route length: ", length_route)
            route_is_feasible = is_feasible(route,couriers,deliveries, distance_matrix)
            if not route_is_feasible:
                print("Route is not feasible")   

        objective = get_objective(initial_solution, couriers, deliveries, distance_matrix)
        print(instance_data['instance_name'], objective)