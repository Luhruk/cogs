import random

class Combat:
    def __init__(self, data_handler):
        self.data_handler = data_handler

    def fight(self, user_id, enemy_name):
        player = self.data_handler.get_user_data(user_id)
        enemy = self.data_handler.load_monster_data().get(enemy_name, None)

        if not enemy:
            return "Enemy not found!"

        while player["health"] > 0 and enemy["health"] > 0:
            # Player attacks
            damage = random.randint(player["strength"] - 2, player["strength"] + 2)
            enemy["health"] -= damage

            # Enemy attacks
            damage = random.randint(enemy["strength"] - 2, enemy["strength"] + 2)
            player["health"] -= damage

            if enemy["health"] <= 0:
                player["xp"] += 100
                player["currency"] += 20
                self.data_handler.save()
                return "You won!"
            elif player["health"] <= 0:
                return "You lost!"
