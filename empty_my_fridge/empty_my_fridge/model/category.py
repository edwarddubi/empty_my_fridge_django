class Category:
    def __init__(self):
        self.category = None
        self.category_page = "1"
        self.is_cat_and_ingrd = False
        self.filter_list = None
        self.sorting_type = "name_A"

    def get_sorting_type(self):
        return self.sorting_type

    def set_sorting_type(self, type):
        self.sorting_type = type

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

    def set_filter_list(self, filters):
        if not filters:
            self.filter_list = None
        elif len(filters) == 0:
            self.filter_list = None
        else:
            self.filter_list = filters

    def get_filter_list(self):
        return self.filter_list