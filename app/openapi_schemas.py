from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from app.serializers import PhotoSerializer, PhotoUpdateSchemaSerializer
from users.serializers import ErrorDetailSerializer

ALBUM_VIEWSET = {
	'list': extend_schema(
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
	'create': extend_schema(summary='Создание альбома'),
	'retrieve': extend_schema(summary='Получение альбома'),
	'partial_update': extend_schema(summary='Редактирование названия альбома'),
	'destroy': extend_schema(summary='Удаление альбома'),
}

PHOTO_VIEWSET = {
	'list': extend_schema(
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
	'create': extend_schema(
		summary='Загрузка фотографии',
		responses={
			201: PhotoSerializer,
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
	'retrieve': extend_schema(summary='Получение фотографии'),
	'partial_update': extend_schema(
		summary='Редактирование названия фотографии и/или тегов',
		request=PhotoUpdateSchemaSerializer,
	),
	'destroy': extend_schema(summary='Удаление фотографии'),
}
