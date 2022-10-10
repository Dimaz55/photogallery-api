from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiExample)
from rest_framework import viewsets, parsers
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter

from app import serializers
from app.filters import PhotoFilter
from app.models import Album, Photo
from app.permissions import IsOwner
from app.serializers import PhotoUpdateSchemaSerializer
from users.serializers import ErrorDetailSerializer


class OwnerOnlyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwner]
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


@extend_schema(tags=['albums'])
@extend_schema_view(
    list=extend_schema(
        summary='Получение списка альбомов',
        parameters=[
            OpenApiParameter(
                name='ordering',
                description='Сортировка по количеству фото в альбоме или дате '
                            'создания',
                location='query',
                enum=['photos_count', 'created_at'],
                many=True)
        ]
    ),
    create=extend_schema(summary='Создание альбома'),
    retrieve=extend_schema(summary='Получение альбома'),
    partial_update=extend_schema(summary='Редактирование названия альбома'),
    destroy=extend_schema(summary='Удаление альбома'),
)
class AlbumViewSet(OwnerOnlyViewSet):
    queryset = Album.objects.prefetch_related('photos')\
                            .annotate(photos_count=Count('photos'))
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'photos_count']
    
    def get_serializer_class(self):
        if self.action in ['list', 'partial_update']:
            return serializers.AlbumListSerializer
        return serializers.AlbumSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Получение списка фотографий',
        parameters=[
            OpenApiParameter(
                name='ordering',
                description='Сортировка по альбому и/или дате загрузки',
                location='query',
                enum=['uploaded_at', 'album'],
                many=True
            )
        ]
    ),
    create=extend_schema(
        summary='Загрузка фотографии',
        responses={
            201: serializers.PhotoSerializer,
            413: ErrorDetailSerializer
        },
        examples=[
            OpenApiExample(
                name='Превышен размер файла',
                value={'detail': 'File size exceeds maximum allowed'},
                response_only=True,
                status_codes=[413]
            )
        ],
    ),
    retrieve=extend_schema(summary='Получение фотографии'),
    partial_update=extend_schema(
        summary='Редактирование названия фотографии и/или тегов',
        request=PhotoUpdateSchemaSerializer,
    ),
    destroy=extend_schema(summary='Удаление фотографии'),
)
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
