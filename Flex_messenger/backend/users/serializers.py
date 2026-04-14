from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User
from typing import cast


class UserSerializer(serializers.ModelSerializer):
    is_online = serializers.SerializerMethodField()
    online_status = serializers.SerializerMethodField()
    last_seen_display = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'date_birth', 'avatar',
                  'created_at', 'last_seen', 'is_online', 'online_status', 
                  'last_seen_display', 'avatar_url']
        read_only_fields = ['id', 'username', 'created_at', 'last_seen']

    def get_is_online(self, obj):
        return obj.is_online

    def get_online_status(self, obj):
        return obj.online_status

    def get_last_seen_display(self, obj):
        return obj.last_seen_display

    def get_avatar_url(self, obj):
        return obj.avatar_url()


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    username = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all(), message="Пользователь с таким логином уже существует")])
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all(), message="Пользователь с таким email уже существует")])
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'date_birth', 'avatar']
        extra_kwargs = {
            'date_birth': {'required': False},
            'avatar': {'required': False, 'allow_null': True},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Пароли не совпадают"})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class UserAuthSerializer(serializers.Serializer):
    """Сериализатор для аутентификации пользователя"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(read_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Неверный логин или пароль")
        if not user.is_active:
            raise serializers.ValidationError("Аккаунт заблокирован")
        user = cast(User, user)
        data['user'] = user
        return data