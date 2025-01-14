import json

class DataHandler:
    def __init__(self, base_path="data/"):
        self.base_path = base_path
        self.player_data = self.load_data("data.json")

    def load_data(self, filename):
        try:
            with open(f"{self.base_path}{filename}", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_data(self, filename, data):
        with open(f"{self.base_path}{filename}", "w") as f:
            json.dump(data, f)

    def load_world_data(self):
        return self.load_data("world.json")

    def load_monster_data(self):
        return self.load_data("monsters.json")

    def load_item_data(self):
        return self.load_data("items.json")

    def load_spell_data(self):
        return self.load_data("spells.json")

    def get_user_data(self, user_id):
        if str(user_id) not in self.player_data:
            self.player_data[str(user_id)] = {}
        return self.player_data[str(user_id)]

    def set_user_data(self, user_id, data):
        self.player_data[str(user_id)] = data
        self.save_data("data.json", self.player_data)
