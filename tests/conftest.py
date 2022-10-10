import tempfile

import pytest
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files import File
from model_bakery import baker
from rest_framework.test import APIClient

from app.models import Album, Photo

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory():
    def factory(**kwargs):
        return baker.make(User, **kwargs)
    return factory


@pytest.fixture
def album_factory():
    def factory(**kwargs):
        return baker.make(Album, **kwargs)
    return factory


@pytest.fixture
def photo_factory():
    def factory(**kwargs):
        return baker.make(Photo, **kwargs)
    return factory


@pytest.fixture
def user_data():
    return {
        'username': 'test_user_name',
        'password': 'SuperPassword'
    }


@pytest.fixture
def photo_file():
    def file(oversize=False):
        image = Image.new('RGB', (1920, 1080))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        if oversize:
            image.save(tmp_file, 'bmp')
        else:
            image.save(tmp_file, 'jpeg')
        tmp_file.seek(0)
        return File(tmp_file)
    return file
