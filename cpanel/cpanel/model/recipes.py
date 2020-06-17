
class Recipes:
    def __init__(self, recipe_list):
        self.recipe_list = recipe_list
        self.pos = 0

    def __init__(self):
        self.recipe_list = None
        self.pos = 0

    def get_all_recipes(self):
        return self.recipe_list

    def set_all_recipes(self, recipe_list):
        self.recipe_list = recipe_list

    def set_recipe_list_position(self, pos):
        self.pos = pos

    def get_recipe_list_position(self):
        return self.pos            
