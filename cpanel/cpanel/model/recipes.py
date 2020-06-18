
class Recipes:
    def __init__(self, recipe_list):
        self.recipe_list = recipe_list
        self.pos = 0
        self.liked = False
        self.searched = False
        self.word_to_filter = None
        self.recipes_current_page = "1"

    def __init__(self):
        self.recipe_list = None
        self.pos = 0
        self.liked = False
        self.searched = False
        self.word_to_filter = None
        self.recipes_current_page = "1"

    def get_all_recipes(self):
        return self.recipe_list

    def set_all_recipes(self, recipe_list):
        self.recipe_list = recipe_list

    def set_recipe_list_position(self, pos):
        self.pos = pos

    def get_recipe_list_position(self):
        return self.pos

    def set_is_recipe_liked(self, liked):
        self.liked = liked

    def get_is_recipe_liked(self):
        return self.liked

    def set_is_searched_for_recipes(self, searched):
        self.searched = searched

    def get_is_searched_for_recipes(self):
        return self.searched

    def set_word_to_filter(self, word):
        self.word_to_filter = word

    def get_word_to_filter(self):
        return self.word_to_filter

    def set_recipes_current_page(self, page):
        self.recipes_current_page = page    

    def get_recipes_current_page(self):
        return self.recipes_current_page                        
