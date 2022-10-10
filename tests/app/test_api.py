import os
import shutil
import time
import pytest
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode

from app.models import Album, Photo
from config import settings


@pytest.mark.django_db
class TestAlbum:
    
    def test_create_album(self, api_client, user_factory):
        album_count = Album.objects.count()
        user = user_factory()
        api_client.force_authenticate(user=user)
        url = reverse('albums-list')
        response = api_client.post(url, data={'title': 'Test title'})
        assert response.status_code == 201
        assert 'title' in response.json()
        assert response.json()['title'] == 'Test title'
        assert Album.objects.count() == album_count + 1
    
    def test_create_album_without_title(self, api_client, user_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)
        url = reverse('albums-list')
        response = api_client.post(url, data={'title': ''})
        assert response.status_code == 400
    
    def test_create_album_without_authentication(
            self, api_client, user_factory):
        url = reverse('albums-list')
        response = api_client.post(url, data={'title': 'Test title'})
        assert response.status_code == 401
    
    def test_list_albums(self, api_client, user_factory, album_factory):
        user = user_factory()
        albums = album_factory(_quantity=5, owner=user)
        api_client.force_authenticate(user=user)
        url = reverse('albums-list')
        response = api_client.get(url)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == len(albums)
    
    def test_retrieve_album(self, api_client, user_factory, album_factory):
        user = user_factory()
        album = album_factory(owner=user)
        api_client.force_authenticate(user=user)
        url = reverse('albums-detail', kwargs={'pk': album.pk})
        response = api_client.get(url)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert response.json()['id'] == album.id
        assert response.json()['title'] == album.title
        assert response.json()['owner'] == user.username
    
    def test_retrieve_album_not_owned_by_user(
            self, api_client, user_factory, album_factory):
        user = user_factory(_quantity=2)
        album = album_factory(owner=user[0])
        api_client.force_authenticate(user=user[1])
        url = reverse('albums-detail', kwargs={'pk': album.pk})
        response = api_client.get(url)
        assert response.status_code == 404
    
    def test_update_album_title(
            self, api_client, user_factory, album_factory):
        user = user_factory()
        album = album_factory(owner=user)
        api_client.force_authenticate(user=user)
        url = reverse('albums-detail', kwargs={'pk': album.pk})
        response = api_client.patch(url, data={'title': 'New title'})
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert response.json()['title'] == 'New title'
    
    def test_update_album_readonly_fields(
            self, api_client, user_factory, album_factory):
        user = user_factory()
        album = album_factory(owner=user)
        api_client.force_authenticate(user=user)
        url = reverse('albums-detail', kwargs={'pk': album.pk})
        data = {
            'owner': 'test_user',
            'created_at': '2000-01-01 01:01:01',
            'photos_amount': -1
        }
        response = api_client.patch(url, data=data)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert response.json()['owner'] == album.owner.username
        assert response.json()['created_at'] == \
               album.created_at.strftime("%Y-%m-%d %H:%M:%S")
        assert response.json()['photos_amount'] == album.photos_amount
    
    def test_delete_own_album(
            self, api_client, user_factory, album_factory):
        user = user_factory()
        album = album_factory(owner=user)
        album_count_before = Album.objects.count()
        api_client.force_authenticate(user=user)
        url = reverse('albums-detail', kwargs={'pk': album.pk})
        response = api_client.delete(url)
        assert response.status_code == 204
        assert Album.objects.count() == album_count_before - 1
    
    def test_delete_album_not_owned_by_user(
            self, api_client, user_factory, album_factory):
        user = user_factory(_quantity=2)
        album = album_factory(owner=user[0])
        album_count_before = Album.objects.count()
        api_client.force_authenticate(user=user[1])
        url = reverse('albums-detail', kwargs={'pk': album.pk})
        response = api_client.delete(url)
        assert response.status_code == 404
        assert Album.objects.count() == album_count_before

    @pytest.mark.parametrize(
        'ordering_field, model_field, index0, index1',
        [
            ('created_at', 'created_at', 1, 0),
            ('-created_at', 'created_at', 0, 1),
            ('photos_count', 'photos_amount', 1, 0),
            ('-photos_count', 'photos_amount', 0, 1),
        ]
    )
    def test_album_ordering(self, api_client, user_factory, photo_factory,
                            album_factory, photo_file, ordering_field, index0,
                            index1, model_field):
        user = user_factory()
        album1 = album_factory(owner=user)
        photo_factory(_quantity=1, album=album1, owner=user, photo=photo_file())
        time.sleep(1)
        album2 = album_factory(owner=user)
        photo_factory(_quantity=3, album=album2, owner=user, photo=photo_file())
        api_client.force_authenticate(user=user)
        query_params = {'ordering': ordering_field}
        url = reverse('albums-list') + '?' + urlencode(query_params)
        response = api_client.get(url)
        assert response.json()[index0][model_field] > \
               response.json()[index1][model_field]


@pytest.mark.django_db
class TestPhoto:
    
    def test_list_owner_photos(self, api_client, user_factory, album_factory,
                               photo_factory, photo_file):
        user = user_factory(_quantity=2)
        photos_of_user1 = photo_factory(
            _quantity=10, owner=user[0], photo=photo_file())
        photos_of_user2 = photo_factory(
            _quantity=5, owner=user[1], photo=photo_file())
        api_client.force_authenticate(user=user[0])
        url = reverse('photos-list')
        response = api_client.get(url)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == len(photos_of_user1)
    
    def test_retrieve_own_photo(self, api_client, user_factory, album_factory,
                                photo_factory, photo_file):
        user = user_factory()
        album = album_factory()
        photo = photo_factory(owner=user, album=album, photo=photo_file())
        api_client.force_authenticate(user=user)
        url = reverse('photos-detail', kwargs={'pk': photo.pk})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.json()['title'] == photo.title
        assert response.json()['album'] == photo.album.pk

    def test_retrieve_not_owned_photo(self, api_client, user_factory,
                                      album_factory, photo_factory, photo_file):
        user = user_factory(_quantity=2)
        album = album_factory(owner=user[0])
        photo = photo_factory(owner=user[0], album=album, photo=photo_file())
        api_client.force_authenticate(user=user[1])
        url = reverse('photos-detail', kwargs={'pk': photo.pk})
        response = api_client.get(url)
        assert response.status_code == 404
    
    def test_create_photo_in_album_not_owned_by_user(
            self, api_client, user_factory, album_factory, photo_file):
        user = user_factory(_quantity=2)
        album = album_factory(owner=user[0])
        photo_count_before = Photo.objects.count()
        data = {
            'title': 'Test photo',
            'album': album.pk,
            'photo': photo_file()
        }
        api_client.force_authenticate(user=user[1])
        url = reverse('photos-list')
        response = api_client.post(url, data=data, format='multipart')
        assert response.status_code == 404
        assert Photo.objects.count() == photo_count_before
        
    def test_create_photo_in_owned_album(
            self, api_client, user_factory, album_factory, photo_file):
        user = user_factory()
        album = album_factory(owner=user)
        photo_count_before = Photo.objects.count()
        data = {
            'title': 'Test photo',
            'album': album.pk,
            'photo': photo_file()
        }
        api_client.force_authenticate(user=user)
        url = reverse('photos-list')
        response = api_client.post(url, data=data, format='multipart')
        assert response.status_code == 201
        assert 'title' in response.json()
        assert response.json()['title'] == data['title']
        assert Photo.objects.count() == photo_count_before + 1

    def test_create_photo_exceeding_maximum_upload_size(
            self, api_client, user_factory, album_factory, photo_file):
        user = user_factory()
        album = album_factory(owner=user)
        photo_count_before = Photo.objects.count()
        data = {
            'title': 'Test photo',
            'album': album.pk,
            'photo': photo_file(oversize=True)
        }
        api_client.force_authenticate(user=user)
        url = reverse('photos-list')
        response = api_client.post(url, data=data, format='multipart')
        assert response.status_code == 413
        assert Photo.objects.count() == photo_count_before

    @pytest.mark.parametrize(
        'ordering_field, index0, index1',
        [
            ('album', 1, 0),
            ('-album', 0, 1),
            ('uploaded_at', 1, 0),
            ('-uploaded_at', 0, 1),
        ]
    )
    def test_photo_ordering(self, api_client, user_factory, photo_factory,
                            album_factory, photo_file, ordering_field, index0,
                            index1):
        user = user_factory()
        album1 = album_factory(owner=user)
        photo_factory(album=album1, owner=user, photo=photo_file())
        time.sleep(1)
        album2 = album_factory(owner=user)
        photo_factory(album=album2, owner=user, photo=photo_file())
        api_client.force_authenticate(user=user)
        query_params = {'ordering': ordering_field}
        url = reverse('photos-list') + '?' + urlencode(query_params)
        response = api_client.get(url)
        if ordering_field.startswith('-'):
            ordering_field = ordering_field[1:]
        assert response.json()[index0][ordering_field] > \
               response.json()[index1][ordering_field]
        
    def test_photo_filter_by_tags(self, api_client, user_factory, photo_factory,
                                  album_factory, photo_file):
        user = user_factory()
        album = album_factory()
        photo = Photo(owner=user, album=album, photo=photo_file())
        photo.save()
        photo.tags.add('test1')
        photo = Photo(owner=user, album=album, photo=photo_file())
        photo.save()
        photo.tags.add('test2')
        photo = Photo(owner=user, album=album, photo=photo_file())
        photo.save()
        photo.tags.add('test1', 'test2')
        api_client.force_authenticate(user=user)
        query_params = {'tags': 'test1'}
        url = reverse('photos-list') + '?' + urlencode(query_params)
        response = api_client.get(url)
        assert len(response.json()) == 2
        for item in response.json():
            assert 'test1' in item['tags']
    
    def test_update_own_photo(self, api_client, user_factory, album_factory,
                                photo_factory, photo_file):
        user = user_factory()
        album = album_factory()
        photo = photo_factory(owner=user, album=album, photo=photo_file())
        api_client.force_authenticate(user=user)
        url = reverse('photos-detail', kwargs={'pk': photo.pk})
        data = {
            'title': 'Updated title',
            'tags': ['new tag 1', 'new tag 2']
        }
        response = api_client.patch(url, data=data)
        assert response.status_code == 200
        assert response.json()['title'] == data['title']
        assert set(response.json()['tags']) == set(data['tags'])

    def test_update_photo_readonly_fields(self, api_client, user_factory,
                                          album_factory, photo_factory,
                                          photo_file):
        user = user_factory(_quantity=2)
        album = album_factory()
        photo = photo_factory(owner=user[0], album=album, photo=photo_file())
        time.sleep(1)
        api_client.force_authenticate(user=user[0])
        url = reverse('photos-detail', kwargs={'pk': photo.pk})
        data = {
            'owner': user[1].username,
            'uploaded_at': timezone.now()
        }
        response = api_client.patch(url, data=data)
        assert response.json()['owner'] == user[0].username
        assert response.json()['uploaded_at'] == \
               photo.uploaded_at.strftime("%Y-%m-%d %H:%M:%S")
    
    def test_delete_own_photo(self, api_client, user_factory, album_factory,
                              photo_factory, photo_file):
        user = user_factory()
        album = album_factory()
        photo = photo_factory(owner=user, album=album, photo=photo_file())
        photo_count_before = Photo.objects.count()
        api_client.force_authenticate(user=user)
        url = reverse('photos-detail', kwargs={'pk': photo.pk})
        response = api_client.delete(url)
        assert response.status_code == 204
        assert Photo.objects.count() == photo_count_before - 1
