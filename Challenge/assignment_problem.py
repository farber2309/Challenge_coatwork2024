import numpy as np
from scipy.optimize import linear_sum_assignment
import time

from feasibility_checker import get_route_cost, Route, is_feasible
from simulated_annealing import get_objective
from read_data import process_all_instances
from first_solution import generate_initial_solution


# Function to solve the assignment problem
def assign_couriers_to_deliveries(couriers, deliveries, distance_matrix_between_locations):
    # Number of couriers and deliveries
    num_couriers = len(couriers)
    num_deliveries = len(deliveries)

    # Define a large cost for infeasible assignments (due to capacity constraints)
    infeasible_cost = 1e6

    # Create a distance matrix between couriers and deliveries
    distance_matrix = np.zeros((num_couriers, num_deliveries))
    for i, courier in enumerate(couriers):
        for j, delivery in enumerate(deliveries):
            if courier.capacity < delivery.capacity:
                # Set a high cost if courier's capacity is insufficient for the delivery
                distance_matrix[i][j] = infeasible_cost
            else:
                route = Route(courier.courier_id, [])
                route.stops.append(delivery.delivery_id)   # Append pickup (positive delivery ID)
                route.stops.append(delivery.delivery_id) 
                route_cost = get_route_cost(route, couriers, deliveries, distance_matrix_between_locations)
                distance_matrix[i][j] = route_cost
            

    # Solve the assignment problem using the Hungarian algorithm
    return linear_sum_assignment(distance_matrix)


if __name__ == "__main__":
    training_data_folder = "training_data"
    all_instance_data = process_all_instances(training_data_folder)

    for instance in all_instance_data:
        
        couriers = instance['couriers']
        deliveries = instance['deliveries']
        distance_matrix = np.array(instance['travel_time'])

        # check if the number of couriers is less than the number of deliveries
        if len(couriers) > len(deliveries):
            print("Instance", instance['instance_name'])
            #print("Number of couriers", len(couriers), "is greater than the number of deliveries", len(deliveries))
            

            # remove first line and first column
            distance_matrix = distance_matrix[1:, 1:]
            distance_matrix = distance_matrix.astype(int)

            initial_solution = generate_initial_solution(couriers, deliveries)
            for route in initial_solution:
                route_is_feasible = is_feasible(route,couriers,deliveries)
                if not route_is_feasible:
                    print("Route is not feasible")   
            initial_objective = get_objective(initial_solution, couriers, deliveries, distance_matrix)

            size_nbh = 3
            start_time = time.time()
            row_indices, col_indices = assign_couriers_to_deliveries(couriers, deliveries, distance_matrix)
            end_time = time.time()

            routes = [Route(courier.courier_id, []) for courier in couriers]
            offset_courirer = - 1 # courier id: from 1 to x included
            offset_delivery = len(couriers) + 1 # delivery id: from x+1 to x+y included
            for row, col in zip(row_indices, col_indices):
                courirer_id = row + offset_courirer
                delivery_id = col + offset_delivery
                routes[row].stops.append(delivery_id)
                routes[row].stops.append(delivery_id)


            assignment_objective = get_objective(routes, couriers, deliveries, distance_matrix)

            if initial_objective < assignment_objective:
                print(instance['instance_name'], ": initial objective", initial_objective, " is better than assignment objective", assignment_objective)
            else:
                print(instance['instance_name'], ": assignment objective", assignment_objective, " is better than initial objective", initial_objective)

        
        # else:
        #     print("Number of couriers is less than the number of deliveries")