from django_filters import rest_framework as filters

from app.models import Photo


class PhotoFilter(filters.FilterSet):
    album = filters.BaseInFilter(
        field_name='album_id', help_text='Фильтрация по id альбома')
    tags = filters.BaseInFilter(
        field_name='tags__name', help_text='Фильтрация по тегам')

    class Meta:
        model = Photo
        fields = ['album', 'tags']
