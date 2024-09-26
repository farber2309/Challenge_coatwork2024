import os
import csv
# import argparse
from Route import *
from Delivery import *
from Courier import * 

#########################################################
#
# collection of various useful functions 
# 
#########################################################

def copy_routes(routes):
    new_routes = []
    for route in routes:
        new_route = Route(route.rider_id, route.stops.copy())
        new_routes.append(new_route)
    return new_routes

def copy_route(route):
    return Route(route.rider_id, route.stops.copy())

def get_objective(solution, couriers, deliveries, distance_matrix):
    total_time = 0
    for route in solution:
        total_time += get_route_cost(route, couriers, deliveries, distance_matrix)
    return total_time

def is_all_feasible(solution, couriers, deliveries):
    for route in solution:
        if not is_feasible(route, couriers, deliveries):
            return False
    return True

def get_route_duration(route, couriers, deliveries, travelTimes):
    currentTime = 0
    orders_in_bag = set()
    courier = get_courier(couriers, route.rider_id)
    lastLocation = courier.location
    for activity in route.stops:
        delivery = get_delivery(deliveries, activity)
        if activity in orders_in_bag:
            orders_in_bag.remove(activity)
            currentTime = currentTime + travelTimes[lastLocation - 1][
            delivery.dropoff_loc - 1]
            lastLocation = delivery.dropoff_loc
        else:
            orders_in_bag.add(activity)
            currentTime = max(delivery.time_window_start,
                            currentTime + travelTimes[lastLocation - 1][
                                delivery.pickup_loc - 1])
            lastLocation = delivery.pickup_loc

    return currentTime

# Reading files from csv (given by organizers)

# Function to load couriers from CSV using the csv module
def load_couriers_from_csv(filepath):
    couriers = []
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            courier = Courier(
                courier_id=int(row['ID']),
                location=int(row['Location']),
                capacity=int(row['Capacity'])
            )
            couriers.append(courier)
    return couriers


# Function to load deliveries from CSV using the csv module
def load_deliveries_from_csv(filepath):
    deliveries = []
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            delivery = Delivery(
                delivery_id=int(row['ID']),
                capacity=int(row['Capacity']),
                pickup_loc=int(row['Pickup Loc']),
                time_window_start=int(row['Time Window Start']),
                pickup_stacking_id=int(row['Pickup Stacking_Id']),
                dropoff_loc=int(row['Dropoff Loc'])
            )
            deliveries.append(delivery)
    return deliveries


# Function to load travel time matrix from CSV
def load_travel_time_from_csv(filepath):
    travel_time = []
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == 'Locations':
                travel_time.append([val for val in row])
            else:
                travel_time.append([int(val) for val in row])  # Convert the row values to integers, skip the location index (first column)
    return travel_time


# Function to process each instance folder and look for couriers.csv, deliveries.csv, and traveltime.csv
def process_instance_folder(instance_folder_path):
    couriers_file = None
    deliveries_file = None
    travel_time_file = None

    # Search for files in the instance folder
    for filename in os.listdir(instance_folder_path):
        if 'couriers.csv' in filename:
            couriers_file = os.path.join(instance_folder_path, filename)
        elif 'deliveries.csv' in filename:
            deliveries_file = os.path.join(instance_folder_path, filename)
        elif 'traveltimes.csv' in filename:
            travel_time_file = os.path.join(instance_folder_path, filename)

    # Ensure all necessary files are found
    if not couriers_file:
        raise FileNotFoundError(f"Missing couriers.csv file in folder: {instance_folder_path}")

    if not deliveries_file:
        raise FileNotFoundError(f"Missing deliveries.csv file in folder: {instance_folder_path}")

    if not travel_time_file:
        raise FileNotFoundError(f"Missing traveltimes.csv file in folder: {instance_folder_path}")


    # Load couriers, deliveries, and travel time matrix from the instance
    couriers = load_couriers_from_csv(couriers_file)
    deliveries = load_deliveries_from_csv(deliveries_file)
    travel_time = load_travel_time_from_csv(travel_time_file)

    return couriers, deliveries, travel_time


# Main function to loop through all instance folders
def process_all_instances(parent_folder):
    all_instances = []
    # Loop through each instance folder in the parent directory
    for instance_folder in os.listdir(parent_folder):
        # very small: '0b220d8f-ba16-4848-86ef-b446ef436fce' 1 delivery
        # small: '1adef166-1111-45fd-b722-0f817c7fa055' 2 deliveries
        # large: '0ba3c52f-4d24-4033-be91-5dac2ad16a4f' 745 deliveries
        # if instance_folder != '389f96b3-a8b9-4715-9260-6842e4509073':
        #     continue
        instance_folder_path = os.path.join(parent_folder, instance_folder)

        # Check if it's a directory (instance folder)
        if os.path.isdir(instance_folder_path):
            print(f"Processing instance: {instance_folder}")
            try:
                couriers, deliveries, travel_time = process_instance_folder(instance_folder_path)

                # Add this instance's couriers, deliveries, and travel time matrix to the overall list
                all_instances.append({
                    'instance_name': instance_folder,
                    'couriers': couriers,
                    'deliveries': deliveries,
                    'travel_time': travel_time
                })
            except FileNotFoundError as e:
                print(e)     

    return all_instances

# Feasibility check and other stuff:
def read_routes_from_csv(csv_file):
  routes = []
  if not os.path.exists(csv_file):
    return routes
  with open(csv_file, 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header line
    for row in reader:
      rider_id = int(row[0])
      stops = [int(stop) for stop in row[1:]]
      routes.append(Route(rider_id, stops))
  return routes


def check_all_couriers_covered(routes, couriers):
  n_couriers = len(couriers)
  courier_found = [False] * n_couriers
  all_couriers_covered = True
  for route in routes:
    if courier_found[route.rider_id - 1] == True:
      print(f"Courier {route.rider_id} has more than one route.")
      all_couriers_covered = False
    courier_found[route.rider_id - 1] = True
  for i, has_route in enumerate(courier_found):
    if not has_route:
      print(f"Courier {i + 1} has no route.")
      all_couriers_covered = False
  return all_couriers_covered


def check_all_activities_covered(routes, couriers, deliveries):
  n_couriers = len(couriers)
  n_orders = len(deliveries)
  order_found = [0] * n_orders
  all_activities_are_covered = True
  for route in routes:
    for order in route.stops:
      order_found[order - n_couriers - 1] = order_found[
                                              order - n_couriers - 1] + 1
  for i, order_has_route in enumerate(order_found):
    if order_has_route < 2:
      print(
        f"Order {i + n_couriers + 1} appears less than twice in the solution.")
      all_activities_are_covered = False
    if order_has_route > 2:
      print(
        f"Order {i + n_couriers + 1} appears more than twice in the solution.")
      all_activities_are_covered = False
  return all_activities_are_covered


def is_feasible(route, couriers, deliveries, traveltimes):
  courier = get_courier(couriers, route.rider_id)
  courierCapacity = courier.capacity
  load = 0
  orders_in_bag = set()
  for activity in route.stops:
    delivery = get_delivery(deliveries, activity)
    if activity in orders_in_bag:
      orders_in_bag.remove(activity)
      load = load - delivery.capacity
    else:
      orders_in_bag.add(activity)
      load = load + delivery.capacity
      if load > courierCapacity:
        print(
          f"Route of courier {route.rider_id} violates the capacity condition at pickup {activity}.")
        return False
  if orders_in_bag:
    print(
      f"Route of courier {route.rider_id} only has a pickup for deliveries {orders_in_bag}.")
    return False

  if not check_route_length(route):
    print(
      f"Route of courier {route.rider_id} contains more than four deliveries.")
    return False

  if not check_route_duration(route, couriers, deliveries, traveltimes):
    return False

  return True


def check_route_duration(route, couriers, deliveries, travelTimes):
  currentTime = 0
  orders_in_bag = set()
  courier = get_courier(couriers, route.rider_id)
  lastLocation = courier.location
  for activity in route.stops:
    delivery = get_delivery(deliveries, activity)
    if activity in orders_in_bag:
      orders_in_bag.remove(activity)
      currentTime = currentTime + travelTimes[lastLocation - 1][
        delivery.dropoff_loc - 1]
      lastLocation = delivery.dropoff_loc
    else:
      orders_in_bag.add(activity)
      currentTime = max(delivery.time_window_start,
                        currentTime + travelTimes[lastLocation - 1][
                          delivery.pickup_loc - 1])
      lastLocation = delivery.pickup_loc

  if currentTime > 180:
    print(
      f"Route of courier {route.rider_id} is takes too long with {currentTime} minutes.")
    return False

  return True

def check_route_length(route):
  return len(route.stops) <= 8


def get_route_cost(route, couriers, deliveries, travelTimes):
  courier = get_courier(couriers, route.rider_id)
  currentTime = 0
  cost = 0
  orders_in_bag = set()
  lastLocation = courier.location
  for activity in route.stops:
    delivery = get_delivery(deliveries, activity)
    if activity in orders_in_bag:
      orders_in_bag.remove(activity)
      currentTime = currentTime + travelTimes[lastLocation - 1][
        delivery.dropoff_loc - 1]
      lastLocation = delivery.dropoff_loc
      cost = cost + currentTime
    else:
      orders_in_bag.add(activity)
      currentTime = max(delivery.time_window_start,
                        currentTime + travelTimes[lastLocation - 1][
                          delivery.pickup_loc - 1])
      lastLocation = delivery.pickup_loc
  return cost


def get_courier(couriers, courier_id):
  for courier in couriers:
    if courier.courier_id == courier_id:
      return courier
  return None


# Function to get the delivery by delivery_id
def get_delivery(deliveries, delivery_id):
  for delivery in deliveries:
    if delivery.delivery_id == delivery_id:
      return delivery
  return None