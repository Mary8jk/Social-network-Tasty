from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
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


class CustomUserUpdateSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password')

    def validate(self, attrs):
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        if not current_password or not new_password:
            raise serializers.ValidationError(
                'Both current_password and new_password are required.')
        user = self.context['request'].user
        if not user.check_password(current_password):
            raise serializers.ValidationError('Current password is incorrect.')
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        new_password = validated_data.get('new_password')
        user.set_password(new_password)
        user.save()
        return user


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


class RecipeIngredientDetailSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit",
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    # Создай отдельный сериализатор для ингредиентов и вместо:
    # ingredients = serializers.SerializerMethodField()  используй его. (ревью)
    # вот здесь не поняла как это реализовать, тк в response же список словарей
    # ingredients, но записала короче чем было через staticmethod и новый
    # сериализатор RecipeIngredientDetailSerializer
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

    @staticmethod
    def get_ingredients(obj):
        queryset = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientDetailSerializer(queryset, many=True).data

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
    id = serializers.ReadOnlyField(source='tag.id')

    class Meta:
        model = TagRecipe
        fields = ('id',)


class RecipeIngredientDetailCreateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    # def to_representation(self, instance):
    # В этом нет смысла, судя по всему, просто используй правильный
    # сериализатор во вьюхе. (ревью)
    # тут вроде с полями ingredients и tags разобалась, но поводу
    # def to_representation пока думаю как без него обойтись,
    # я так поняла с помощью
    # to_representation можно подогнать данные к форме ответа
    # в том числе? пока что убрала репрезентейшн
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientDetailCreateSerializer(
        many=True, read_only=True, source='recipeingredient_set')
    tags = TagRecipeSerializer(
        many=True, read_only=True, source='tagrecipe_set')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
                  'image', 'text', 'cooking_time',)

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError('Image field cannot be empty.')
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Cooking time cannot be less than 1 minute.')
        return value


class CustomRecipeSerializer(RecipeListSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='recipes.id', read_only=True)
    name = serializers.CharField(source='recipes.name', read_only=True)
    image = serializers.ImageField(source='recipes.image', read_only=True)
    cooking_time = serializers.IntegerField(source='recipes.cooking_time',
                                            read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='recipe.id', read_only=True)
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(source='recipe.cooking_time',
                                            read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe', 'id', 'name', 'image', 'cooking_time')
        extra_kwargs = {
            'user': {'write_only': True},
            'recipe': {'write_only': True}, }

    def validate(self, data):
        user = data['user']
        if user.shopping_carts.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Recipe already added to the shopping cart')
        return data


class SubscribeSerializer(serializers.ModelSerializer):
    recipes = CustomRecipeSerializer(read_only=True, many=True,
                                     source='following.recipes')
    follow = CustomUserSerializer(read_only=True, source='following')

    class Meta:
        model = Subscribe
        fields = ('follow', 'user', 'following', 'recipes', 'recipes_count',)
        read_only_fields = ('follow',)
        extra_kwargs = {'user': {'write_only': True},
                        'following': {'write_only': True}}
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'following'),
                message='Subscription already exist'
            )
        ]

    def validate(self, data):
        user = data['user']
        following_id = data['following']
        if user == following_id:
            raise serializers.ValidationError(
                'You cannot subscribe to yourself')
        return data

    # здесь репрезентейшн как убрать обертку follow не понятно пока что
    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = instance.following
        recipes_count = Recipe.objects.filter(author=user).count()
        data['recipes_count'] = recipes_count
        return data


class SubscribeListSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        return CustomRecipeSerializer(recipes, many=True).data

    # еее тут разбралась, только надо подумать как getы убрать или не убрать
    class Meta:
        model = User
        fields = CustomUserSerializer.Meta.fields + ('recipes',
                                                     'recipes_count', )
        extra_kwargs = {
            'password': {'write_only': True},
        }
