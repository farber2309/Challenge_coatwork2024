import numpy as np
import time

from feasibility_checker import *
from read_data import process_all_instances
from helpers import get_route_cost, get_route_duration, copy_route, get_objective


def greedy_heuristic(couriers, deliveries, distance_matrix):
    del_offset = len(couriers) + 1
    cou_offset = 1
    time_now = min([delivery.time_window_start for delivery in deliveries])
    
    # At starting time
    couriers_pool = [couriers[i] for i in range(len(couriers))]
    deliveries_pool = [deliveries[i] for i in range(len(deliveries)) if deliveries[i].time_window_start <= time_now]

    routes_solutions = [Route(courier.courier_id, []) for courier in couriers]

    done_delivery = [False for delivery in deliveries]

    #print(time_now, len(deliveries_pool))
    ko=False
    while done_delivery.count(False) > 0:
        #print(done_delivery.count(True))
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
                print("No more feasible assignment", nb_assigned), "over ", len(deliveries_pool)
                ko = True
                break
            routes_solutions[courier_id - cou_offset].stops.append(deliveries_pool[best_delivery_idx].delivery_id)
            routes_solutions[courier_id - cou_offset].stops.append(deliveries_pool[best_delivery_idx].delivery_id)
            cost_matrix[:,best_delivery_idx] = 1e6 # cannot assign the delivery to another courier
            cost_matrix[best_courier_idx,:] = 1e6 # cannot assign the courier to another delivery

            couriers[courier_id - cou_offset].available_time = get_route_duration(routes_solutions[courier_id - cou_offset], couriers, deliveries, distance_matrix)
            # uddate the status of the delivery
            deliveries_pool[best_delivery_idx].done = True
            delivery = deliveries_pool[best_delivery_idx]
            #print(delivery.delivery_id, "assigned to ", courier_id)
            nb_assigned += 1
        
        done_delivery = [delivery.done for delivery in deliveries]

        if ko:
            break

        
        # Update the pools
        if done_delivery.count(False) == 0:
            break
        time_now = min([delivery.time_window_start for delivery in deliveries if not delivery.done])
        #print(time_now, len(deliveries_pool))
        deliveries_pool = [delivery for delivery in deliveries if not delivery.done and delivery.time_window_start <= time_now]

        couriers_pool = [courier for courier in couriers if courier.available_time <= time_now]


    return routes_solutions            


if __name__ == "__main__":
    training_data_folder = "training_data_hard"
    all_instance_data = process_all_instances(training_data_folder)

    for instance in all_instance_data:
        print("Instance name: ", instance['instance_name'])
        couriers = instance['couriers']
        deliveries = instance['deliveries']
        distance_matrix = np.array(instance['travel_time'])
        distance_matrix = distance_matrix[1:, 1:]
        distance_matrix = distance_matrix.astype(int)


        routes_solutions = greedy_heuristic(couriers, deliveries, distance_matrix)
        print("Objective value: ", get_objective(routes_solutions, couriers, deliveries, distance_matrix))
