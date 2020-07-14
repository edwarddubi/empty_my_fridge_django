class Category:
    def __init__(self):
        self.category = None
        self.category_page = "1"
        self.is_cat_and_ingrd = False

    def set_category(self, category):
        self.category = category

    def get_category(self):
        return self.category

    def set_category_page(self, page):
        self.category_page = page

    def get_category_page(self):
        return self.category_page

    def set_cat_and_ingrd(self, is_cat_and_ingrd):
        self.is_cat_and_ingrd = is_cat_and_ingrd

    def get_cat_and_ingrd(self):
        return self.is_cat_and_ingrd