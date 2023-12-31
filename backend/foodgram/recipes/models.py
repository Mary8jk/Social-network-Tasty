from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=60, help_text='name of tag')
    color = models.CharField(max_length=7,
                             help_text='color (ex, #FF0000)')
    slug = models.CharField(max_length=60,
                            help_text='slug')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=60)
    measurement_unit = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='recipes/',
        null=False
    )
    text = models.CharField(max_length=1200)
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         through_fields=(
                                             'recipe', 'ingredient',
                                             'measurement_unit'))
    tags = models.ManyToManyField(Tag, through='TagRecipe')
    cooking_time = models.PositiveIntegerField()

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='recipe_ingredients')
    amount = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.ingredient.name} {self.amount}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites_user')
    recipes = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorite_recipes')

    def __str__(self):
        return f'{self.user} {self.recipes}'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower')
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following')
    recipes_count = models.IntegerField(default=0)
    recipes = models.ManyToManyField(Recipe, related_name='subscribers')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='shopping_carts')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='shopping_carts')


class ShoppingListRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredient = models.ManyToManyField(ShoppingCart,
                                        through='ShoppingListRecipeIngredient',
                                        related_name='shopping_lists')
    amount_needed = models.PositiveIntegerField()
    measurement_unit = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                         related_name='shopping_list_units')


class ShoppingListRecipeIngredient(models.Model):
    shopping_list_recipe = models.ForeignKey(ShoppingListRecipe,
                                             on_delete=models.CASCADE)
    shopping_cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='shopping_list_ingredients')
    amount_needed = models.PositiveIntegerField()
    measurement_unit = models.ForeignKey(Ingredient, on_delete=models.CASCADE)


class TagRecipe(models.Model):
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tags} {self.recipe}'
