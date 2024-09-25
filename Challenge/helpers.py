from feasibility_checker import get_route_cost, Route, is_feasible, get_courier, get_delivery
    
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
