
class Recipes:
    def __init__(self, recipe_list, db):
        self.recipe_list = recipe_list
        self.pos = 0
        self.liked = False
        self.searched = False
        self.recipe_name_to_find = None
        self.recipes_current_page = "1"
        self.word_to_filter = None

    def __init__(self, db):
        self.recipe_list = None
        self.pos = 0
        self.liked = False
        self.searched = False
        self.recipe_name_to_find = None
        self.recipes_current_page = "1"
        self.word_to_filter = None

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

    def set_recipe_name_to_find(self, word):
        self.recipe_name_to_find = word

    def get_recipe_name_to_find(self):
        return self.recipe_name_to_find

    def set_recipes_current_page(self, page):
        self.recipes_current_page = page

    def get_recipes_current_page(self):
        return self.recipes_current_page

    def set_recipe_liked(self, key):
        for recipe in self.recipe_list:
            if recipe["recipe_id"] == key:
                recipe["user_saved"] = True
                recipe["likes"] = recipe["likes"] + 1
                break

    def set_recipe_unLiked(self, key):
        for recipe in self.recipe_list:
            if recipe["recipe_id"] == key:
                recipe["user_saved"] = False
                recipe["likes"] = recipe["likes"] - 1
                break                                     
