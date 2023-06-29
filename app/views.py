from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, parsers
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter

from app import serializers, openapi_schemas
from app.filters import PhotoFilter
from app.models import Album, Photo
from app.permissions import IsOwner


class OwnerOnlyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwner]
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


@extend_schema(tags=['albums'])
@extend_schema_view(**openapi_schemas.ALBUM_VIEWSET)
class AlbumViewSet(OwnerOnlyViewSet):
    queryset = Album.objects\
        .select_related('owner')\
        .prefetch_related('photos', 'photos__tags')\
        .annotate(photos_count=Count('photos'))
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'photos_count']
    
    def get_serializer_class(self):
        if self.action in ['list', 'partial_update']:
            return serializers.AlbumListSerializer
        return serializers.AlbumSerializer


@extend_schema_view(**openapi_schemas.PHOTO_VIEWSET)
@extend_schema(tags=['photos'])
class PhotoViewSet(OwnerOnlyViewSet):
    queryset = Photo.objects.prefetch_related('tags')
    parser_classes = [parsers.MultiPartParser, parsers.JSONParser]
    serializer_class = serializers.PhotoSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PhotoFilter
    ordering_fields = ['uploaded_at', 'album']
    
    def create(self, request, *args, **kwargs):
        album = Album.objects.filter(pk=request.data['album'])
        if not album or album.first().owner != request.user:
            raise NotFound({'detail': 'album not found'})
        return super().create(request, *args, **kwargs)
