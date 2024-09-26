class Courier:
  def __init__(self, courier_id, location, capacity):
    self.courier_id = courier_id
    self.location = location
    self.capacity = capacity
    self.available_time = 0

  def __repr__(self):
    return f"Courier(ID={self.courier_id}, Location={self.location}, Capacity={self.capacity})"