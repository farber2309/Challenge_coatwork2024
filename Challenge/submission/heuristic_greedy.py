import numpy as np
import time

from read_data import process_all_instances
from Route import *
from Delivery import *
from Courier import * 

from helpers import get_route_cost, get_route_duration, copy_route, get_objective, is_all_feasible
# from first_solution import generate_initial_solution
from output_results_to_csv import save_solution
from assignment_problem import run_assignment_problem


def greedy_heuristic(couriers, deliveries, distance_matrix):
    time_init = time.time()
    percentage = 0.0
    del_offset = len(couriers) + 1
    cou_offset = 1

    while True:
        time_now = min([delivery.time_window_start for delivery in deliveries])
        
        # At starting time
        back_couriers_ids = np.random.choice([courier.courier_id for courier in couriers], int(percentage * len(couriers)), replace=False)
        couriers_pool = [couriers[i] for i in range(len(couriers)) if couriers[i].courier_id not in back_couriers_ids]
        deliveries_pool = [deliveries[i] for i in range(len(deliveries)) if deliveries[i].time_window_start <= time_now]
        routes_solutions = [Route(courier.courier_id, []) for courier in couriers]

        done_delivery = [False for delivery in deliveries]
        back = False
        tuple_detection_prev = (done_delivery.count(False), len(couriers_pool), len(deliveries_pool))
        tuple_detection_new = (0, 0, 0)

        while done_delivery.count(False) > 0:
            # print(done_delivery.count(False), len(couriers_pool), len(deliveries_pool))

            # Compute the cost matrix for each rider to each delivery of the pools
            cost_matrix = np.zeros((len(couriers_pool), len(deliveries_pool)))
            for i, courier in enumerate(couriers_pool):
                for j, delivery in enumerate(deliveries_pool):
                    # Check if courier can handle the delivery
                    if courier.capacity < delivery.capacity:
                        cost_matrix[i][j] = 1e6  # High cost to represent invalid assignment
                    else:
                        # Simulate adding the delivery to the courier's route
                        new_route = copy_route(routes_solutions[courier.courier_id - cou_offset])
                        new_route.stops.append(delivery.delivery_id)
                        new_route.stops.append(delivery.delivery_id)
                        
                        # Calculate the route duration and cost
                        route_duration = get_route_duration(new_route, couriers, deliveries, distance_matrix)
                        
                        if route_duration > 180:  # If the route exceeds the max duration
                            cost_matrix[i][j] = 1e16
                        else:
                            cost_matrix[i][j] = get_route_cost(new_route, couriers, deliveries, distance_matrix)
            
            nb_assigned = 0
            while nb_assigned < len(deliveries_pool):
                # Assign the delivery to its best courier
                min_cost_idx = np.unravel_index(np.argmin(cost_matrix), cost_matrix.shape)
                best_courier_idx, best_delivery_idx = min_cost_idx

                courier_id = couriers_pool[best_courier_idx].courier_id
                
                # If value is too high, break the loop
                if cost_matrix[best_courier_idx][best_delivery_idx] >= 1e6:
                    if nb_assigned == 0:
                        back = True
                    break
                routes_solutions[courier_id - cou_offset].stops.append(deliveries_pool[best_delivery_idx].delivery_id)
                routes_solutions[courier_id - cou_offset].stops.append(deliveries_pool[best_delivery_idx].delivery_id)
                cost_matrix[:,best_delivery_idx] = 1e6 # cannot assign the delivery to another courier
                cost_matrix[best_courier_idx,:] = 1e6 # cannot assign the courier to another delivery

                if len(routes_solutions[courier_id - cou_offset].stops) >= 8: # max number of deliveries
                    couriers[courier_id - cou_offset].available_time = 1e6
                else:
                    couriers[courier_id - cou_offset].available_time = get_route_duration(routes_solutions[courier_id - cou_offset], couriers, deliveries, distance_matrix)
                # uddate the status of the delivery
                deliveries_pool[best_delivery_idx].done = True
                delivery = deliveries_pool[best_delivery_idx]
                nb_assigned += 1
            
            done_delivery = [delivery.done for delivery in deliveries]

            # Update the pools
            if done_delivery.count(False) == 0:
                break
            time_now = min([delivery.time_window_start for delivery in deliveries if not delivery.done])

            deliveries_pool = [delivery for delivery in deliveries if not delivery.done and delivery.time_window_start <= time_now]
            couriers_pool = [courier for courier in couriers if courier.available_time <= time_now]
            

            if back and len(back_couriers_ids) != 0:
                i = np.random.choice(range(len(back_couriers_ids)))
                couriers_pool.append(couriers[back_couriers_ids[i]-cou_offset])
                # print("append courier ", back_couriers_ids[i])
                back = False
                back_couriers_ids = np.delete(back_couriers_ids, i)
                

            while len(couriers_pool) == 0:
                # print("len courier pool updated")
                time_now = time_now + 1
                couriers_pool = [courier for courier in couriers if courier.available_time <= time_now]

                
            tuple_detection_new = (done_delivery.count(False), len(couriers_pool), len(deliveries_pool))
            if tuple_detection_new == tuple_detection_prev:
                # print("Detected stagnation, restarting with higher percentage.")
                if percentage == 0.0:
                    percentage = 0.05 
                percentage += 0.05
                for courier in couriers:
                    courier.available_time = 0 
                for delivery in deliveries:
                    delivery.done = False
                break  # Exit the current while loop and restart with higher percentage
            tuple_detection_prev = tuple_detection_new
        
        # Check if all deliveries are done
        if done_delivery.count(False) == 0:
            break

    return routes_solutions            


if __name__ == "__main__":
    np.random.seed(123456)
    training_data_folder = "final_test_set"
    all_instance_data = process_all_instances(training_data_folder)

    for instance in all_instance_data:
        print("Instance name: ", instance['instance_name'])
        routes_solutions = []

        # Instance data
        couriers = instance['couriers']
        deliveries = instance['deliveries']
        distance_matrix = np.array(instance['travel_time'])
        distance_matrix = distance_matrix[1:, 1:]
        distance_matrix = distance_matrix.astype(int)

        assigment_sol = []
        assigment_obj = 9e6
        if len(couriers) > len(deliveries):
            assigment_sol = run_assignment_problem(couriers, deliveries, distance_matrix)
            feasibility = is_all_feasible(assigment_sol, couriers, deliveries, distance_matrix)
            if feasibility:
                assigment_obj = get_objective(assigment_sol, couriers, deliveries, distance_matrix)
                print("Objective value assignment: ", assigment_obj)
            else:
                print("error in assignment")

        
        dummy_sol = []
        dummy_obj = 9e6

        # greedy heuristic
        greedy_sol = greedy_heuristic(couriers, deliveries, distance_matrix)
        feasibility = is_all_feasible(greedy_sol, couriers, deliveries, distance_matrix)
        print("Feasibility greedy: ", feasibility)
        greedy_obj = 9e6
        if feasibility:
            greedy_obj = get_objective(greedy_sol, couriers, deliveries, distance_matrix)
            print("Objective value heuristic: ", greedy_obj)
        # else:
        #     print("Infeasible solution with heuristic greedy")
        #     # Dummy solution
        #     dummy_sol = generate_initial_solution(couriers, deliveries, distance_matrix)
        #     feasibility = is_all_feasible(dummy_sol, couriers, deliveries, distance_matrix)
        #     dummy_obj = 1e6
        #     if feasibility:
        #         obj_val = get_objective(dummy_sol, couriers, deliveries, distance_matrix)
        #     print("Objective value of dummy solution: ", dummy_obj)

        # Simulated annealing
        # best_solution, best_objective = simulated_annealing(routes_solutions, initial_temp=1000, cooling_rate=0.995, max_iterations=2000, size_neighborhood=2, couriers=couriers, deliveries=deliveries, distance_matrix=distance_matrix)
        # feasibility = is_all_feasible(best_solution, couriers, deliveries, distance_matrix)
        # if feasibility:
        #     sa_obj_val = get_objective(best_solution, couriers, deliveries, distance_matrix)
        #     print("Objective value simulated annealing: ", sa_obj_val)


        
        # Save the solution
        output_folder_path = "./final_solutions_test"
        instance_folder_path = './' + training_data_folder + '/' + instance['instance_name']
        if greedy_obj < assigment_obj:
            courier_order = [[delivery_id for delivery_id in route.stops] for route in greedy_sol]
        # else assigment_obj < dummy_obj:
        #     courier_order = [[delivery_id for delivery_id in route.stops] for route in assigment_sol]
        # else:
        #     courier_order = [[delivery_id for delivery_id in route.stops] for route in dummy_sol]
            
        save_solution(courier_order, instance_folder_path, output_folder_path)
