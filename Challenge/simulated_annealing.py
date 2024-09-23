import numpy as np
import random
import math

from read_data import process_all_instances
from feasibility_checker import get_route_cost, Route, is_feasible

# Function to generate the initial solution
def generate_initial_solution(couriers, deliveries):
    # Create a list of Route objects for each courier
    routes = [Route(courier.courier_id, []) for courier in couriers]
    
    # Distribute deliveries among couriers
    for i, delivery in enumerate(deliveries):
        courier_idx = i % len(couriers)  # Distribute deliveries equally among couriers
        route = routes[courier_idx]  # Get the Route object for this courier
        
        # Append the delivery pickup and drop-off to the courier's route (Route.stops)
        route.stops.append(delivery.delivery_id)   # Append pickup (positive delivery ID)
        route.stops.append(delivery.delivery_id)  # Append dropoff (negative delivery ID)

    # Print initial solution
    # for route in routes:
    #     print(route)

    return routes

# Calculate the total distance of a given route
def calculate_distance(route):
    total_distance = 0
    current_location = 0  # Start at the depot
    for rider_route in route:
        for location in rider_route:
            total_distance += distance_matrix[current_location][location]
            current_location = location
        total_distance += distance_matrix[current_location][0]  # Return to depot
        current_location = 0  # Reset for the next rider
    return total_distance

# Swap two locations in the route
def swap(route):
    new_route = [rider_route.copy() for rider_route in route]
    rider_idx = random.randint(0, num_riders - 1)
    if len(new_route[rider_idx]) > 1:  # Ensure there is something to swap
        idx1, idx2 = random.sample(range(len(new_route[rider_idx])), 2)
        new_route[rider_idx][idx1], new_route[rider_idx][idx2] = new_route[rider_idx][idx2], new_route[rider_idx][idx1]
    return new_route

# Simulated annealing algorithm
def simulated_annealing(initial_solution, initial_temp, cooling_rate, max_iterations):
    current_solution = initial_solution
    current_distance = calculate_distance(current_solution)
    best_solution = current_solution
    best_distance = current_distance

    temperature = initial_temp

    for iteration in range(max_iterations):
        new_solution = swap(current_solution)
        new_distance = calculate_distance(new_solution)
        
        # Acceptance probability
        if new_distance < current_distance or random.uniform(0, 1) < math.exp((current_distance - new_distance) / temperature):
            current_solution = new_solution
            current_distance = new_distance
            
            if current_distance < best_distance:
                best_solution = current_solution
                best_distance = current_distance

        temperature *= cooling_rate  # Cool down

    return best_solution, best_distance

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
    total_cost = 0
    for route in initial_solution:
        route_is_feasible = is_feasible(route,couriers,deliveries)
        total_cost += get_route_cost(route, couriers, deliveries, distance_matrix)

    print("Initial solution cost:", total_cost)

    #best_solution, best_distance = simulated_annealing(initial_solution, initial_temp=1000, cooling_rate=0.995, max_iterations=10000)

    # # Format output as specified
    # formatted_solution = []
    # for rider in range(num_riders):
    #     commands = best_solution[rider]
    #     formatted_solution.append([commands, [], []])  # Placeholder for order and additional info

    # print("Best solution:", formatted_solution)
    # print("Best distance:", best_distance)
