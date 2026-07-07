from django.db import models

from reviews.constants import MODELS_MAX_LENGTH


class NameSlugModel(models.Model):
    """Абстрактная модель с полями name и slug."""

    name = models.CharField(
        max_length=MODELS_MAX_LENGTH,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор'
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class PublishedModel(models.Model):
    """Абстрактная модель с полями текста, автора и даты публикации."""

    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    author = models.ForeignKey(
        'reviews.User',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Автор отзыва'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации отзыва'
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} от {self.author}'
