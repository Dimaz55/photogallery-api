import os

from django.contrib.admin import display
from django.contrib.auth.models import User
from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from taggit.managers import TaggableManager

from config import settings


def get_photo_upload_path(instance, filename):
    return f'user_{instance.owner.id}/album_{instance.album.id}/{filename}'


def get_thumbnail_upload_path(instance, filename):
    return f'user_{instance.owner.id}/album_{instance.album.id}/' \
           f'thumbnails/thumb_{filename}'


class Album(models.Model):
    title = models.CharField('Название альбома', max_length=255)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
        related_name='albums'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    @display(description='Кол-во фото')
    def photos_amount(self) -> int:
        return self.photos.count()
    
    def __str__(self):
        return f'{self.title} ({self.id})'
    
    class Meta:
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'
        

class Photo(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец'
    )
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        verbose_name='Альбом',
        related_name='photos'
    )
    title = models.CharField(
        'Название', max_length=255)
    photo = models.ImageField('Фото', upload_to=get_photo_upload_path)
    thumbnail = ThumbnailerImageField(
        'Миниатюра',
        upload_to=get_thumbnail_upload_path,
        resize_source=dict(size=(150, 150), sharpen=True))
    tags = TaggableManager('Теги', blank=True)
    uploaded_at = models.DateTimeField('Дата загрузки', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'
    
    def save(self, *args, **kwargs):
        if self.photo.file is not None:
            self.thumbnail = self.photo.file
        return super().save(*args, **kwargs)
    