from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, generics, mixins
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound, NotAuthenticated
from rest_framework.response import Response

from users import examples
from users.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    ErrorDetailSerializer
)


class UserRegistrationView(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    
    @extend_schema(
        summary='Регистрация нового пользователя',
        responses={
            201: UserRegistrationSerializer,
            400: ErrorDetailSerializer
        },
        examples=[
            examples.REGISTRATION_SUCCESS,
            examples.USER_EXISTS
        ]
    )
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']
        user = User.objects.create(**serializer.validated_data)
        user.set_password(password)
        user.save()
        return Response(self.serializer_class(user).data, status=201)


class UserLoginView(generics.CreateAPIView):
    serializer_class = UserLoginSerializer
    
    @extend_schema(
        summary='Аутентификация (получение токена)',
        responses={
            200: UserLoginSerializer,
            400: ErrorDetailSerializer,
            401: ErrorDetailSerializer
        },
        examples=[
            examples.LOGIN_SUCCESS,
            examples.USER_NOT_FOUND,
            examples.WRONG_PASSWORD
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = User.objects.filter(username=username)
        if not user:
            raise NotFound({'detail': 'user not found'})
        if not user or not user.first().check_password(password):
            raise NotAuthenticated({'detail': 'wrong credentials'})
        token, _ = Token.objects.get_or_create(user=user.first())
        return Response({'token': token.key})
