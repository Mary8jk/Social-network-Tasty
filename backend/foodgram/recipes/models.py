from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=60, help_text="Название тэга")
    color = models.CharField(max_length=7,
                             help_text="Цвет тэга (например, '#FF0000')")
    slug = models.CharField(max_length=60,
                            help_text="Уникальный идентификатор тэга")

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=60)
    amount = models.IntegerField(null=True)
    measurement_unit = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    text = models.CharField(max_length=1200)
    ingredient = models.ManyToManyField(Ingredient, related_name='recipes')
    tag = models.ManyToManyField(Tag, related_name='recipes')
    cooking_time = models.IntegerField()

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe, related_name='favorites')


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower')
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following')

    def __str__(self):
        return str(self.user)


class ShoppingListIngredient(models.Model):
    shopping_list = models.ForeignKey(
        'ShoppingCart',
        on_delete=models.CASCADE,
        related_name='ingredients_for_buy'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='shopping_lists'
    )
    amount = models.IntegerField()


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(
        ShoppingListIngredient,
        related_name='shopping_carts')
