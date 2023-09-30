from django.contrib import admin
from .models import Recipe, Tag, Ingredient, Favorite, ShoppingCart, Subscribe, RecipeIngredient, ShoppingListRecipe, ShoppingListRecipeIngredient, TagRecipe


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class TagInline(admin.TabularInline):
    model = Tag
    extra = 1


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tag', 'ingredients',)

    inlines = [RecipeIngredientInline]
    inlines_2 = [TagInline]


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite)
admin.site.register(Subscribe)
admin.site.register(ShoppingCart)
admin.site.register(RecipeIngredient)
admin.site.register(ShoppingListRecipe)
admin.site.register(ShoppingListRecipeIngredient)
admin.site.register(TagRecipe)
