from django.db import models
from django import forms

class Search(models.Model):
    search_bar = models.CharField(max_length=50)
    def __str__(self):
        return self.search_bar


class Fridge(models.Model):
    ingredients =  []
    owned = forms.BooleanField()
    class Meta:
        db_table = "all_ingredients"

    def _get_ingredients(self):
        return self.ingredients

    def _add(self, food):
        return self.ingredients.append(food)

    def _remove(self, food):
        return self.ingredients.remove(food)
