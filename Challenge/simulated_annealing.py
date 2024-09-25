import numpy as np
import random
import math
import time

from read_data import process_all_instances
from feasibility_checker import is_feasible
from first_solution import generate_initial_solution
from helpers import *


def remove_delivery_from_route(route, delivery_id):
    # Remove the delivery from the route
    route.stops.remove(delivery_id)

def shift_delivery_in_route(route, delivery_id, action: bool, size: int):
    print("route before shifting: ", route.stops)
    # route is the original route
    idx_delivery = []
    for i, stop in enumerate(route.stops):
        if stop == delivery_id:
            idx_delivery.append(i)
            if len(idx_delivery) == 2:
                break
    idx_pick = idx_delivery[0]
    idx_drop = idx_delivery[1]

    if action: # move pick up
        neighborhood_start = max(0, idx_pick - size)
        neighborhood_end = min(idx_drop, idx_pick + size)
        new_idx = random.randint(neighborhood_start, neighborhood_end)
        route.stops.insert(new_idx, route.stops.pop(idx_pick))

    else: # move drop off
        neighborhood_start = max(idx_pick, idx_drop - size)
        neighborhood_end = min(len(route.stops), idx_drop + size)
        new_idx = random.randint(neighborhood_start, neighborhood_end)
        route.stops.insert(new_idx, route.stops.pop(idx_drop))
    
    print("route after shifting: ", route.stops)

    print("Is route feasible: ", is_feasible(route, couriers, deliveries))

def change_delivery_route(route, delivery_id, new_route):
    # Find the pickup and dropoff indices for the delivery
    idx_delivery = []
    for i, stop in enumerate(route.stops):
        if stop == delivery_id:
            idx_delivery.append(i)
            if len(idx_delivery) == 2:
                break

    idx_pick = idx_delivery[0]
    idx_drop = idx_delivery[1]

    # Remove both pickup and dropoff from the original route
    # Dropoff needs to be removed before pickup to maintain correct indices
    route.stops.pop(idx_drop)
    route.stops.pop(idx_pick)

    # Insert them at random positions in the new route
    new_pick_idx = random.randint(0, len(new_route.stops))  # Random position for pickup
    new_route.stops.insert(new_pick_idx, delivery_id)  # Insert pickup

    new_drop_idx = random.randint(new_pick_idx + 1, len(new_route.stops))  # Ensure dropoff is after pickup
    new_route.stops.insert(new_drop_idx, delivery_id)  # Insert dropoff

    print("Is route feasible: ", is_feasible(new_route, couriers, deliveries))



def swap_delivery(routes, size):
    # Choose two random routes
    random_route_remove = random.randint(0, len(routes) - 1)
    
    # Ensure the chosen route has at least one stop
    while len(routes[random_route_remove].stops) == 0:
        random_route_remove = random.randint(0, len(routes) - 1)

    random_route_add = random.randint(0, len(routes) - 1)

    # Ensure the two routes are different and the removing route has enough deliveries
    while random_route_remove == random_route_add and len(routes[random_route_remove].stops) <= 2:
        random_route_add = random.randint(0, len(routes) - 1)

    #print("Routes chosen are ", random_route_remove, random_route_add)
    #print("Route before swapping: ", routes[random_route_remove].stops, routes[random_route_add].stops)

    # If it's the same route, shift the delivery within the same route
    if random_route_remove == random_route_add:  # Same route
        random_idx = random.randint(0, len(routes[random_route_remove].stops) - 1)
        delivery_id = routes[random_route_remove].stops[random_idx]  # Randomly choose a delivery to shift
        
        # Ensure the same delivery is not selected multiple times
        action = random.choice([True, False])  # Randomly decide to shift pickup or drop off
        shift_delivery_in_route(routes[random_route_remove], delivery_id, action, size)

    else:  # Different routes: remove from one route and add to another
        random_idx = random.randint(0, len(routes[random_route_remove].stops) - 1)
        delivery_id = routes[random_route_remove].stops[random_idx]  # Randomly choose a delivery to remove

        # Check if the delivery already exists in the target route to avoid duplicating it
        if delivery_id in routes[random_route_add].stops:
            print(f"Delivery {delivery_id} already exists in the target route, no swap made.")
        else:
            # Move the delivery to the new route
            change_delivery_route(routes[random_route_remove], delivery_id, routes[random_route_add])
    
    #print("Route after swapping: ", routes[random_route_remove].stops, routes[random_route_add].stops)

    return routes



# Simulated annealing algorithm
def simulated_annealing(initial_solution, initial_temp, cooling_rate, max_iterations, size_neighborhood=1):
    current_solution = initial_solution
    current_objective = get_objective(current_solution, couriers, deliveries, distance_matrix)
    best_solution = copy_routes(current_solution)  # Create a deep copy of the initial solution
    best_objective = current_objective

    temperature = initial_temp

    for iter in range(max_iterations):
        print ("iteration: ", iter, "objective: ", current_objective, 'best objective: ', best_objective)
        
        # Copy the current solution before modifying it
        new_solution = copy_routes(current_solution)  # Copy before calling swap_delivery
        new_solution = swap_delivery(new_solution, size_neighborhood)  # Modify the copy instead of current_solution
        new_objective = get_objective(new_solution, couriers, deliveries, distance_matrix)
        #print('current objective: ', current_objective)
        #print("new objective after swap: ", new_objective)
        
        # Acceptance probability
        if new_objective < current_objective or random.uniform(0, 1) < math.exp((current_objective - new_objective) / temperature):
            current_solution = new_solution  # Update the current solution if accepted
            current_objective = new_objective
            
            if current_objective < best_objective and is_all_feasible(current_solution, couriers, deliveries):
                best_solution = copy_routes(current_solution)  # Update best_solution with a copy
                best_objective = current_objective

        temperature *= cooling_rate  # Cool down

    return best_solution, best_objective



if __name__ == "__main__":
    training_data_folder = "training_data"
    all_instance_data = process_all_instances(training_data_folder)

    couriers = all_instance_data[0]['couriers']
    deliveries = all_instance_data[0]['deliveries']
    distance_matrix = np.array(all_instance_data[0]['travel_time'])

    # remove first line and first column
    distance_matrix = distance_matrix[1:, 1:]
    distance_matrix = distance_matrix.astype(int)

    initial_solution = generate_initial_solution(couriers, deliveries)
    for route in initial_solution:
        route_is_feasible = is_feasible(route,couriers,deliveries)
        if not route_is_feasible:
            print("Route is not feasible")   

    objective = get_objective(initial_solution, couriers, deliveries, distance_matrix)
    print("Initial objective:", objective)

    size_nbh = 3
    start_time = time.time()
    best_solution, best_objective = simulated_annealing(initial_solution, initial_temp=1000, cooling_rate=0.995, max_iterations=10000, size_neighborhood=size_nbh)
    end_time = time.time()
    print("Best solution:", best_solution)
    print("Best objective:", best_objective)

    print('Is best solution feasible: ', is_all_feasible(best_solution, couriers, deliveries))
    print('Objective of best solution: ', get_objective(best_solution, couriers, deliveries, distance_matrix))
    print('Time taken: ', end_time - start_time)

    # # Format output as specified
    # formatted_solution = []
    # for rider in range(num_riders):
    #     commands = best_solution[rider]
    #     formatted_solution.append([commands, [], []])  # Placeholder for order and additional info

    # print("Best solution:", formatted_solution)
    # print("Best distance:", best_distance)
