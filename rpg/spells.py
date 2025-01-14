class Spells:
    def __init__(self, data_handler):
        self.data = data_handler.load_spell_data()

    def get_spell(self, spell_name):
        return self.data.get(spell_name, "Spell not found!")

    def list_spells(self):
        return list(self.data.keys())
