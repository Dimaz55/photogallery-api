from django.contrib import admin
from django.contrib.admin import display
from django.utils.html import format_html

from app import models


@admin.register(models.Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'photos_amount', 'owner']
    list_display_links = ['id', 'title']


@admin.register(models.Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'photo_link', 'thumb_link', 'tag_list',
                    'album', 'uploaded_at']
    list_display_links = ['title']
    list_filter = ['album', 'owner']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    @display(description='Теги')
    def tag_list(self, obj):
        def tag_wrapper(tag):
            return (
                f'<p style="padding: 0.2em; '
                f'background-color: #79aec8; '
                f'color: white; font-weight: bold; '
                f'border-radius: 5px;'
                f'display: inline-block;">{tag}</p>'
            )
        return format_html(
            '&nbsp;'.join(tag_wrapper(o.name) for o in obj.tags.all())
        )
    
    @display(description='Фотография')
    def photo_link(self, obj):
        return format_html(
            f'<a href="{obj.photo}" target="blank" '
            f'title="Фото откроется в новом окне">Просмотр</a>')

    @display(description='Миниатюра')
    def thumb_link(self, obj):
        return format_html(
            f'<a href="{obj.thumbnail}" target="blank" '
            f'title="Фото откроется в новом окне">Просмотр</a>')
    
    