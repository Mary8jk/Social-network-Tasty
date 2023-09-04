from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


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


