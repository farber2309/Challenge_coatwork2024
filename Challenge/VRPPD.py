from read_data import *
from feasibility_checker import * 
import pyscipopt as scip

import itertools
import numpy as np


import random

class VRPPD:
    # problem variables
    # Deliveries
    deliveries = None
    # name alias for deliveries
    orders = None
    # Couriers
    couriers = None
    # Travel Times
    travel_time = None
    instance_folder_path = ""

    # variables for the mip and lp solvers
    COURIERS = None
    DEPOS = []
    CAPACITIES = []
    ORDERS = []
    PICKUPS = []
    DROPOFFS = []
    SIZES = {} 
    TWSTART = []
    # sum of all travel times
    T = None
    # name alias
    SUM_TRAVEL_TIMES = None

    VERTICES = []
    A1 = []
    A2 = []
    A3 = []
    A4 = []
    DISTANCES = []

    # solution
    routes = None


    def __init__(self):
        pass
    
    def read(self , instance_folder_path):
        # read in data
        self.instance_folder_path = instance_folder_path
        print(instance_folder_path)
        [self.couriers, self.deliveries , self.travel_time] = process_instance_folder(instance_folder_path)
        # name alias for deliveries
        self.orders = self.deliveries

        self.routes = [None] * len(self.couriers)
        for i in range(len(self.couriers)):
            self.routes[i] = Route(rider_id = self.couriers[i].courier_id , stops = [])

        # Fill it with the data for the MIP
        self.COURIERS = [i for i in range(len(self.couriers))]
        for i in self.COURIERS:
            self.DEPOS.append(self.couriers[i].location)
            self.CAPACITIES.append(self.couriers[i].capacity)
        self.MAXCAP = max(self.CAPACITIES)
        self.ORDERS = [i for i in range(len(self.orders))]

        for i in self.ORDERS:
            self.PICKUPS.append(self.orders[i].pickup_loc)
            self.DROPOFFS.append(self.orders[i].dropoff_loc)
            self.SIZES[self.orders[i].pickup_loc] = self.orders[i].capacity 
            self.SIZES[self.orders[i].dropoff_loc] =  - self.orders[i].capacity 
            self.TWSTART.append(self.orders[i].time_window_start)

        VERTICES= list(set(self.DEPOS + self.PICKUPS + self.DROPOFFS))

        A_1 = [(u,v) for u,v in zip(self.DEPOS, self.PICKUPS)]
        A_2 = [(u,v) for u,v in zip(self.PICKUPS, self.DROPOFFS) if u!=v]
        A_3 = [(u,v) for u,v in zip(self.DROPOFFS, self.DEPOS)]
        A_4 = [(u,u) for u in self.DEPOS]

        DISTANCES = np.array(self.travel_time)[1:,1:].astype(np.int16)

        # defined as a sum all of travel time - just an arbitrary large number 
        self.T = np.sum(DISTANCES.flatten())
        # name alias
        self.SUM_TRAVEL_TIMES = self.T
        

    def write(self , dest):
        # dest is the name of the destination
        # open the file
        # write first line with the table head
        # generate string to be written into file
        out = ""
        out += "ID\n"
        for route in self.routes:
            out += str(route.rider_id)
            # if route is an empty list
            if not route.stops:
                out += "\n"
                continue
            else:
                for delivery in route.stops:
                    out += ","
                    out += str(delivery)
                out += "\n"
        with open(dest, 'w+') as file:
            file.write(out)
        return
    
    def mip_solve(self):
        model = scip.Model()

        t = {}
        for i in self.VERTICES:
                t[i] = model.addVar(vtype="C", name=f't[{i}]')

        q= {}
        for i in self.VERTICES:
                q[i] = model.addVar(vtype="C", name=f'q[{i}]', ub=MAXCAP)

        x={}
        for i in self.VERTICES:
            for j in self.VERTICES:
                for k in self.COURIERS:
                        x[i,j,k]= model.addVar(vtype='B', name=f'x[{i},{j},{k}]')

        # 2
        # every vertex should be visited only ones 
        for v in self.VERTICES:
            model.addCons(scip.quicksum(x[i,v,k] for i in self.VERTICES for k in self.COURIERS) == 1)

        # 3 
        # the same vehicle that visits a vertex does also leave it 
        for v in self.VERTICES :
            for k in self.COURIERS:
                    model.addCons(scip.quicksum(x[v,u,k] for u in self.VERTICES)- scip.quicksum(x[u,v,k] for u in self.VERTICES) == 0)

        # 4 
        # guarantee that the same vehicle that visits a
        # pickup vertex does also visit the corresponding delivery vertex

        for o in self.ORDERS:
                for k in self.COURIERS:
                        model.addCons(scip.quicksum(x[u,self.PICKUPS[o],k] for u in self.VERTICES) - scip.quicksum(x[u, self.DROPOFFS[o],k] for u in self.VERTICES) == 0)

        # 5 
        # only the vehicle corresponding to its depot can leave it 
        for k in self.COURIERS:
            model.addCons(scip.quicksum(x[self.DEPOS[k],v,k] for v in self.VERTICES) ==1) 

        # 6
        # ensure that the time variables for the vertices are correctly updated 
        # A1 from depos to pickup
        # A2 form pickup to dropoff (u!=v)

        A_1 = [(u,v) for u in self.DEPOS for v in self.PICKUPS]
        A_2 = [(u,v) for u in self.PICKUPS for v in self.DROPOFFS if u!=v]

        for k in self.COURIERS:
            for arc in list(set(A_1 + A_2)):
                    u,v = arc[0],arc[1]      
                    model.addCons(t[u] + (self.DISTANCES[u-1,v-1] + self.T)*x[u,v,k] <= t[v] + self.T)
                    

        # 7 
        # ensure that the pickup is visited before the corresponding dropoff.
        for o in self.ORDERS:
            model.addCons(t[self.DROPOFFS[o]] - t[self.PICKUPS[o]] >= self.DISTANCES[self.DROPOFFS[o]-1,self.PICKUPS[o]-1])

        # 8 

        # A3 from dropoff to depos 
        # A4 loops on starts 

        for k in self.COURIERS:
            for arc in list(set(A_1 + A_2)):
                    u,v = arc[0],arc[1]
                    model.addCons(q[u] + (self.SIZES[v] + self.MAXCAP)*x[u,v,k] <= q[v] + self.MAXCAP)

        # 9 
        # load at the depots is already fixed
        for k in self.COURIERS:
            model.addCons(q[self.DEPOS[k]]== self.CAPACITIES[k])

        # 10 
        # t is representing the time when a vertex is visited by a vehicle. As we can see, this
        # variable has to respect the bounds of the respective time window.

        for o in ORDERS:
            model.addCons(t[PICKUPS[o]]>= TWSTART[o])
            
        model.setObjective(quicksum(t[v] for v in DROPOFFS))
            

        model.optimize() 
        if model.getNSols() == 0:
            print("No feasible solution found.")
        else:
            print(f'Objective value={model.getObjVal()}')
            print(f'Solution: x={model.getBestSol()}')  

        return
    
    def lp_solve(self , x):
        # x : binary variablesabout which courier is taking which route
        # solve lp for a given set of binaries variables
        # only minimize with respect to the continuous variables
        model = scip.Model()

        t = {}
        for i in self.VERTICES:
            t[i] = model.addVar(vtype="C", name=f't[{i}]')

        q = {}
        for i in self.VERTICES:
            q[i] = model.addVar(vtype="C", name=f'q[{i}]', ub= self.MAXCAP)

        # add constraints
        A_1 = [(u,v) for u in self.DEPOS for v in self.PICKUPS]
        A_2 = [(u,v) for u in self.PICKUPS for v in self.DROPOFFS if u!=v]

        for k in self.COURIERS:
            for arc in list(set(A_1 + A_2)):
                u,v = arc[0],arc[1]
                model.addCons(t[u] + (self.DISTANCES[u-1,v-1] + self.T)*x[u,v,k] <= t[v] + self.T)

        for o in self.ORDERS:
            model.addCons(t[self.DROPOFFS[o]] - t[self.PICKUPS[o]] >= self.DISTANCES[self.DROPOFFS[o]-1,self.PICKUPS[o]-1])
        for k in self.COURIERS:
            for arc in list(set(A_1 + A_2)):
                u,v = arc[0],arc[1]
                model.addCons(q[u] + (self.SIZES[v] + self.MAXCAP)*x[u,v,k] <= q[v] + self.MAXCAP)
        for k in self.COURIERS:
            model.addCons(q[self.DEPOS[k]] == self.CAPACITIES[k])

        for o in self.ORDERS:
            model.addCons(t[self.PICKUPS[o]]>= self.TWSTART[o])
      
        model.setObjective(scip.quicksum(t[v] for v in self.DROPOFFS))
        model.optimize() 
        if model.getNSols() == 0:
            print("No feasible solution found.")
        else:
            print(f'Objective value={model.getObjVal()}')
            print(f'Solution: x={model.getBestSol()}')
        return

    def is_feasible(self):
        for route in self.routes:
            if not is_feasible(route , self.couriers, self.deliveries):
                return False
        return True
    
    def get_init_sol(self):
        # code taken from simulated_annealing.py
        # Create a list of Route objects for each courier
        self.routes = [Route(courier.courier_id, []) for courier in self.couriers]
        
        # Distribute deliveries among couriers
        for i, delivery in enumerate(self.deliveries):
            courier_idx = i % len(self.couriers)  # Distribute deliveries equally among couriers
            route = self.routes[courier_idx]  # Get the Route object for this courier
            
            # Append the delivery pickup and drop-off to the courier's route (Route.stops)
            route.stops.append(delivery.delivery_id)   # Append pickup (positive delivery ID)
            route.stops.append(delivery.delivery_id)  # Append dropoff (negative delivery ID)
    
    def nopt(self , nopt_param):
         self.get_init_sol()
         for route in self.couriers:
              pass
         return


    def divide_conquer_nopt(self , nr_subinstances , nopt_param):
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
    for route in prob.routes:
        # add randomly long list filled with random entries
        # create random list
        nr_iter = random.randint(0, 10)
        random_list = [0] * nr_iter
        for iter in range(nr_iter):
            random_list[iter] = random.randint(1,10)
            # write random list into the routes
        ind = prob.routes.index(route)
        prob.routes[ind].stops = random_list

    prob.write("test_output.csv")

def test_read_routes():
    print("### test_read_routes ###")
    filename = "test_output.csv"
    routes = read_routes_from_csv(filename)
    print(routes)

def test_is_feasible():
    instance_folder = "training_data/1af15032-e729-4759-9329-0cadc6309f5a"
    file_name_routes = "test_output.csv"
    prob = VRPPD()
    prob.read(instance_folder)

    # Create a list of Route objects for each courier
    prob.get_init_sol()

    print(prob.is_feasible())


# print("Test read\n")
# test_read()

# test_routes_output()
# test_write()

# test_read_routes()

test_is_feasible()