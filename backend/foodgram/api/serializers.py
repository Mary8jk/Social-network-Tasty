from djoser.serializers import UserSerializer
from rest_framework import serializers
from users.models import User
from recipes.models import Tag, Recipe, Ingredient, RecipeIngredient, Subscribe


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
            'password': {'write_only': True},  # Скрыть пароль при GET запросе
        }


# class SubscribeSerializer(serializers.ModelSerializer):
#     follow = CustomUserSerializer(source='following', read_only=True)

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         data.pop("user", None)
#         data.pop("following", None)
#         return CustomUserSerializer(instance.following, context=self.context).data

#     class Meta:
#         model = Subscribe
#         fields = ('user', 'following', 'follow')


class SubscribeSerializer(serializers.ModelSerializer):
    follow = CustomUserSerializer(source='following', read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        user = obj.following
        recipes = Recipe.objects.filter(author=user)
        return RecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        user = obj.following
        recipes_count = Recipe.objects.filter(author=user).count()
        return recipes_count

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("user", None)
        data.pop("following", None)
        data['recipes'] = self.get_recipes(instance)  # Добавляем поле 'recipes'
        data['recipes_count'] = self.get_recipes_count(instance)  # Добавляем поле 'recipes_count'
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
    recipe_ingredients = RecipeIngredientSerializer(many=True,
                                                    source='recipeingredient_set')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'recipe_ingredients')


# class SubscribeSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Subscribe
#         fields = ('user', 'following')


class RecipeSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=True)
    author = CustomUserSerializer(
        read_only=True, default=serializers.CurrentUserDefault())
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

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






# from rest_framework import serializers
# from users.models import User


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'username', 'email', 'first_name', 'last_name',
#                   'password')
