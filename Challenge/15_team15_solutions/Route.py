class Route:
    rider_id = None
    stops = []
    times = []
    nr_stops = 0
    capacities = [0]

    def __init__(self, rider_id = None, stops = [] , times = [], nr_stops = 0 , capacities = [0]):
        self.rider_id = rider_id
        self.stops = stops
        # the times taken to reach the corresponding stop
        self.times = times
        # number of stops
        self.nr_stops = len(self.stops)
        # the capacities at the corresponding stop
        self.capacities = capacities

    def __repr__(self):
        return f"Rider ID: {self.rider_id} - Stops: {self.stops}"
  