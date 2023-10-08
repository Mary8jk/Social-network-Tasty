from djoser.serializers import UserSerializer
from rest_framework import serializers
from users.models import User
from recipes.models import Subscribe


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
