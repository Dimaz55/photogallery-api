from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import build_array_type
from rest_framework import serializers
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)
from app.models import Photo, Album


class PhotoSerializer(TaggitSerializer, serializers.ModelSerializer):
    photo = serializers.FileField()
    thumbnail = serializers.FileField(read_only=True)
    album = serializers.PrimaryKeyRelatedField(queryset=Album.objects.all())
    album_title = serializers.CharField(source='album.title', read_only=True)
    owner = serializers.StringRelatedField(read_only=True)
    tags = TagListSerializerField(
        required=False, help_text='["tag1", "tag2", ...]'
    )
    uploaded_at = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S'
    )
    
    class Meta:
        model = Photo
        fields = [
            'id', 'title', 'photo', 'thumbnail', 'album', 'album_title',
            'owner', 'tags', 'uploaded_at'
        ]


class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S'
    )
    
    class Meta:
        model = Album
        fields = [
            'id', 'title', 'owner', 'created_at', 'photos_amount', 'photos'
        ]
        read_only_fields = ['owner', 'created_at']
    
    
class AlbumListSerializer(AlbumSerializer):
    class Meta:
        model = Album
        fields = ['id', 'title', 'owner', 'created_at', 'photos_amount']


class PhotoUpdateSchemaSerializer(serializers.Serializer):
    title = serializers.CharField()
    tags = serializers.CharField(help_text='["tag1", "tag2", ...]')


class CategoryFieldFix(OpenApiSerializerFieldExtension):
    target_class = 'taggit.serializers.TagListSerializerField'

    def map_serializer_field(self, auto_schema, direction):
        return build_array_type(["string"])
