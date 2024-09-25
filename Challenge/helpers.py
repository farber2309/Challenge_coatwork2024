from feasibility_checker import get_route_cost, Route, is_feasible
    
def copy_routes(routes):
    new_routes = []
    for route in routes:
        new_route = Route(route.rider_id, route.stops.copy())
        new_routes.append(new_route)
    return new_routes

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
