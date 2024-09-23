from read_data import *

import random

class VRPPD:
    # problem variables
    # Deliveries
    deliveries = None
    # Couriers
    couriers = None
    # Travel Times
    travel_time = None
    instance_folder_path = ""

    # solution
    routes = []


    def __init__(self):
        pass
    
    def read(self , instance_folder_path):
        # read in data
        self.instance_folder_path = instance_folder_path
        print(instance_folder_path)
        [self.couriers, self.deliveries , self.travel_time] = process_instance_folder(instance_folder_path)
        for courier in self.couriers:
            self.routes.append([courier , []])

    def write(self , dest):
        # dest is the name of the destination
        # open the file
        # write first line with the table head
           # generate string to be written into file
        out = ""
        out += "ID\n"
        for ( courier , route ) in self.routes:
            out += str(courier.courier_id)
            # if route is an empty list
            if not route:
                out += "\n"
                continue
            else:
                for delivery in route:
                    out += ","
                    out += str(delivery)
                out += "\n"
        with open(dest, 'w') as file:
            file.write(out)
        return
    
    def mip_solve(self):
        # declare continuous and binary variables

        # define the respective constraints

        # define the objective

        # solve the mip

        # write into data structure

        return

    def is_feasible(self):
        pass

    def divide_conquer_nopt(self , nr_subinstances , nopt_param -> Int):
        # separate the couriers and orders in randomly selected small sets
        nr_couriers = len(self.couriers)
        nr_deliveries = len(self.deliveries)


        # THIS IS LIKELY BAD, USE MORE INTELLIGENT DISTRIBUTION OF ORDERS AND COURIERS

        # generate list of sublists of roughly equal length
        length_sublist_courier = nr_couriers / nr_subinstances
        length_sublist_delivery = nr_deliveries / nr_subinstances

        # create sublists with None as placeholder
        sublists_couriers   = [None] * length_sublist_courier
        sublists_deliveries = [None] * length_sublist_delivery

        # fill the courier sublists 
        for i in range(nr_subinstances - 1):
            sublists_couriers[i] = self.couriers[i * length_sublist_courier : (i + 1) * length_sublist_courier]
        
        sublists_couriers[nr_subinstances - 1] = self.couriers[(nr_subinstances - 1) * length_sublist_courier : ]

        # fill the delivery sublists
        for i in range(nr_subinstances - 1):
            sublists_deliveries[i] = self.deliveries[i * length_sublist_delivery : (i + 1) * length_sublist_delivery]
        
        sublists_deliveries[nr_subinstances - 1] = self.deliveries[(nr_subinstances - 1) * length_sublist_delivery : ]

        # create subproblem instances
        array_subproblems = [None] * nr_subinstances
        for instance in range(nr_subinstances):
            array_subproblems[instance] = VRPPD()
            array_subproblems[instance].deliveries = sublists_deliveries[instance]

            array_subproblems[instance].couriers = sublists_couriers[instance]

            array_subproblems[instance].travel_time = self.travel_time

        # solve the linear program for each subproblems
        for subproblem in array_subproblems:
            subproblem.mip_solve()

        # partition of couriers and orders
        # TODO

        # solve the linear program generated from the reduced problem
        return 
    def __str__(self):
        out = ""
        out += "### Deliveries ###\n"
        out += str(self.deliveries) + "\n"
        out += "### Couriers ###\n"
        out += str(self.couriers) + "\n"
        out += "### Travel Time ###\n"
        out += str(self.travel_time) + "\n"
        return out


def test_read():
    instance_folder = "training_data/1af15032-e729-4759-9329-0cadc6309f5a"

    prob = VRPPD()
    prob.read(instance_folder)
    print(prob)

def test_routes_output():
    instance_folder = "training_data/1af15032-e729-4759-9329-0cadc6309f5a"
    prob = VRPPD()
    prob.read(instance_folder)
    print(prob.routes)

def test_write():
    instance_folder = "training_data/1af15032-e729-4759-9329-0cadc6309f5a"
    prob = VRPPD()
    prob.read(instance_folder)

    # fill the routes with random entries
    for pair in prob.routes:
        # add randomly long list filled with random entries
        # create random list
        nr_iter = random.randint(0, 10)
        random_list = [0] * nr_iter
        for iter in range(nr_iter):
            random_list[iter] = random.randint(1,10)
            # write random list into the routes
        ind = prob.routes.index(pair)
        prob.routes[ind][1] = random_list

    prob.write("output.csv")


# print("Test read\n")
# test_read()

# test_routes_output()
test_write()