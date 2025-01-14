class Quests:
    def __init__(self, data_handler):
        self.data_handler = data_handler

    def accept_quest(self, user_id, quest_name):
        user_data = self.data_handler.get_user_data(user_id)
        if "quests" not in user_data:
            user_data["quests"] = []
        user_data["quests"].append(quest_name)
        self.data_handler.save()

    def complete_quest(self, user_id, quest_name):
        user_data = self.data_handler.get_user_data(user_id)
        if quest_name in user_data["quests"]:
            user_data["quests"].remove(quest_name)
            user_data["xp"] += 50
            self.data_handler.save()
            return f"Quest {quest_name} completed!"
        return "Quest not found!"
