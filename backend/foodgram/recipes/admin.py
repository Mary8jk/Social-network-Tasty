from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, ShoppingListRecipe,
                     ShoppingListRecipeIngredient, Subscribe, Tag, TagRecipe)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class TagInline(admin.TabularInline):
    model = Tag
    extra = 1


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags', 'ingredients',)

    inlines = [RecipeIngredientInline]
    inlines_2 = [TagInline]


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite)
admin.site.register(Subscribe)
admin.site.register(ShoppingCart)
admin.site.register(RecipeIngredient)
admin.site.register(ShoppingListRecipe)
admin.site.register(ShoppingListRecipeIngredient)
admin.site.register(TagRecipe)
