from django.contrib import admin
from .models import Recipe, Tag, Ingredient, Favorite, ShoppingCart, Subscribe


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_count')
    search_fields = ('ingredient',)
    list_filter = ('name', 'author', 'tag',)

    def favorite_count(self, obj):
        return obj.favorites.all().count()


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Favorite)
admin.site.register(Subscribe)
admin.site.register(ShoppingCart)
