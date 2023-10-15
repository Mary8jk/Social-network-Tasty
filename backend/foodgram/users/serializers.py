from djoser.serializers import UserSerializer
from recipes.models import Subscribe
from rest_framework import serializers
from users.models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            is_subscribed = Subscribe.objects.filter(
                user=request.user, following=obj).exists()
            return is_subscribed
        return False

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
        )
        data = {
            'email': user.email,
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name, }
        return data

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class CustomTokenObtainSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = User.objects.get(email=email)
            if user.check_password(password):
                data = {'email': email}
                return data
            else:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError(
                'Must include email and password.')


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
