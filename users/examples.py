import random
import string

from drf_spectacular.utils import OpenApiExample

LOGIN_SUCCESS = OpenApiExample(
    name='Успех',
    value={'token': ''.join(
        random.choice(string.digits + string.ascii_lowercase) for _ in range(40))},
    status_codes=[200],
    response_only=True,
)

USER_NOT_FOUND = OpenApiExample(
    name='Пользователь не найден',
    value={'detail': 'user not found'},
    status_codes=[404],
    response_only=True,
)

USER_EXISTS = OpenApiExample(
    name='Пользователь уже зарегистрирован',
    value={'detail': 'user with username already registered'},
    status_codes=[400],
    response_only=True,
)

WRONG_PASSWORD = OpenApiExample(
    name='Неверный логин или пароль',
    value={'detail': 'wrong credentials'},
    status_codes=[401],
    response_only=True,
)

REGISTRATION_SUCCESS = OpenApiExample(
    name='Успешная регистрация',
    status_codes=[201],
    response_only=True,
)
