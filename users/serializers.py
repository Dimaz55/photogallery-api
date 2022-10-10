from django.contrib.auth.models import User
from django.core import validators
from rest_framework import serializers


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[
            validators.MinLengthValidator(
                8, 'Пароль должен содержать не менее 8-ми символов')
        ])
    date_joined = serializers.DateTimeField(
        read_only=True, format="%Y-%m-%d %H:%M:%S")
    
    class Meta:
        model = User
        fields = ['username', 'password', 'date_joined']


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    token = serializers.CharField(read_only=True)


class ErrorDetailSerializer(serializers.Serializer):
    detail = serializers.JSONField()
