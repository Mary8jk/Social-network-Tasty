from djoser.serializers import UserSerializer
from rest_framework import serializers
from users.models import User
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Tag, Recipe, Ingredient,
                            RecipeIngredient, Subscribe, Favorite,
                            TagRecipe, ShoppingCart)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            is_subscribed = Subscribe.objects.filter(
                user=request.user, following=obj).exists()
            return is_subscribed
        return False

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class SubscribeSerializer(serializers.ModelSerializer):
    follow = CustomUserSerializer(source='following', read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        user = obj.following
        recipes = Recipe.objects.filter(author=user)
        return RecipeListSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        user = obj.following
        recipes_count = Recipe.objects.filter(author=user).count()
        return recipes_count

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("user", None)
        data.pop("following", None)
        data['recipes'] = self.get_recipes(instance)
        data['recipes_count'] = self.get_recipes_count(instance)
        return data

    class Meta:
        model = Subscribe
        fields = ('user', 'following', 'follow', 'recipes', 'recipes_count')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')


class IngredientSerializer(serializers.ModelSerializer):
    recipe_ingredients = RecipeIngredientSerializer(
        many=True, source='recipeingredient_set')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'recipe_ingredients')


class IngredientListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeListSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=True)
    author = CustomUserSerializer(
        read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tag', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        recipe_ingredients = obj.recipeingredient_set.all()
        ingredients_data = [{
            'id': recipe_ingredient.ingredient.id,
            'name': recipe_ingredient.ingredient.name,
            'measurement_unit': recipe_ingredient.ingredient.measurement_unit,
            'amount': recipe_ingredient.amount}
            for recipe_ingredient in recipe_ingredients
        ]
        return ingredients_data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorite_recipes.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_carts.filter(user=request.user).exists()


class TagRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagRecipe
        fields = ('tag', 'recipe')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    image = Base64ImageField()

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError('Image field cannot be empty.')
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Cooking time cannot be less than 1 minute.')
        return value

    def to_representation(self, instance):
        recipe_serializer = RecipeListSerializer(instance)
        recipe_data = recipe_serializer.data
        result_data = {}
        result_data.update(recipe_data)
        return result_data

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=obj)
        ingredients_list = []

        for recipe_ingredient in recipe_ingredients:
            ingredient = recipe_ingredient.ingredient
            ingredients_list.append({
                'id': ingredient.id,
                'amount': recipe_ingredient.amount
            })
        if len(ingredients_list) > 0:
            return ingredients_list
        else:
            raise serializers.ValidationError("Ingredients cannot be empty.")

    def get_tags(self, obj):
        if isinstance(obj, dict):
            return obj.get('tags')
        tag_recipes = obj.tagrecipe_set.all()
        tag_ids = [tag_recipe.tag.id for tag_recipe in tag_recipes]
        if len(tag_ids) > 0:
            return tag_ids
        else:
            raise serializers.ValidationError("Tags cannot be empty.")


class CustomRecipeSerializer(RecipeListSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        custom_data = {
            'id': data['id'],
            'name': data['name'],
            'image': instance.image.url if instance.image else '',
            'cooking_time': data['cooking_time'],
        }
        return custom_data


class FavoriteSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    recipes = CustomRecipeSerializer()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(data['recipes'])
        del data['recipes']
        data.pop('user', None)
        return data

    class Meta:
        model = Favorite
        fields = ('user', 'recipes')


class RecipeShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        if user.shopping_carts.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Recipe already added to the shopping cart')
        return data

    def to_representation(self, instance):
        return RecipeShoppingCartSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
