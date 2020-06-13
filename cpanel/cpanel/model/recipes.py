
class Recipes:
    def __init__(self, recipe_list):
        self.recipe_list = recipe_list

    def __init__(self):
        self.recipe_list = None

    def get_all_recipes(self):
        return self.recipe_list

    def set_all_recipes(self, recipe_list):
        self.recipe_list = recipe_list        