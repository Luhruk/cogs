class World:
    def __init__(self, data_handler):
        self.data = data_handler.load_world_data()

    def get_location(self, location_id):
        return self.data.get(location_id, "Location not found!")

    def list_locations(self):
        return list(self.data.keys())
