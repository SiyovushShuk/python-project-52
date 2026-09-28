from django.db import models


class Status(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Имя')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        ordering = ['id']
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return self.name
