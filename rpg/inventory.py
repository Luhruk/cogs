class Inventory:
    def __init__(self, data_handler):
        self.data_handler = data_handler

    def add_item(self, user_id, item_name):
        user_data = self.data_handler.get_user_data(user_id)
        user_data["inventory"].append(item_name)
        self.data_handler.save()

    def view_inventory(self, user_id):
        user_data = self.data_handler.get_user_data(user_id)
        return user_data["inventory"]
