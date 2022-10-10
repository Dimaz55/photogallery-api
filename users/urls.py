from django.urls import path

from users.views import UserLoginView, UserRegistrationView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('register/', UserRegistrationView.as_view(
        {'post': 'create'}), name='user-registration')
]
