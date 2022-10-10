from django.contrib.auth.models import User
from django.urls import reverse


class TestUsers:
    def test_create_user(self, db, api_client, user_data):
        user_count = User.objects.count()
        url = reverse('user-registration')
        response = api_client.post(url, data=user_data)
        assert response.status_code == 201
        assert 'username' in response.json()
        assert 'date_joined' in response.json()
        assert User.objects.count() == user_count + 1
    
    def test_create_user_already_exists(self, db, api_client, user_factory):
        user = user_factory()
        user_data = {
            'username': user.username,
            'password': 'random_password'
        }
        url = reverse('user-registration')
        response = api_client.post(url, data=user_data)
        assert response.status_code == 400
    
    def test_user_login(self, db, api_client, user_factory):
        user = user_factory()
        password = User.objects.make_random_password()
        user.set_password(password)
        user.save()
        
        url = reverse('user-login')
        response = api_client.post(
            url, data={'username': user.username, 'password': password})
        assert response.status_code == 200
        response_json = response.json()
        assert isinstance(response_json['token'], str)
    
    def test_user_login_wrong_password(self, db, api_client, user_factory):
        user = user_factory()
        password = User.objects.make_random_password()
        user.set_password(password)
        user.save()
        
        url = reverse('user-login')
        response = api_client.post(
            url, data={'username': user.username, 'password': password + 'a'})
        assert response.status_code == 401
