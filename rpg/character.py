class Character:
    def __init__(self, data_handler):
        self.data_handler = data_handler

    def create_character(self, user_id, class_name):
        classes = {
            "warrior": {"health": 100, "strength": 15, "defense": 10, "magic": 5},
            "mage": {"health": 80, "strength": 5, "defense": 5, "magic": 20},
            "rogue": {"health": 90, "strength": 10, "defense": 8, "magic": 10},
        }

        if class_name.lower() not in classes:
            return "Invalid class!"

        self.data_handler.set_user_data(user_id, {
            "class": class_name.lower(),
            "health": classes[class_name.lower()]["health"],
            "strength": classes[class_name.lower()]["strength"],
            "defense": classes[class_name.lower()]["defense"],
            "magic": classes[class_name.lower()]["magic"],
            "level": 1,
            "xp": 0,
            "inventory": [],
            "currency": 0,
        })
        return f"Character created as {class_name.title()}!"
