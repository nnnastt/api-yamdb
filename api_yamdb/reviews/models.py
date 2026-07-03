from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Category(models.Model):
    """Модель категории произведения."""

    name = models.CharField(
        max_length=256,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Идентификатор'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    """Модель жанра произведения."""

    name = models.CharField(
        max_length=256,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Идентификатор'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения'
    )
    year = models.IntegerField(
        verbose_name='Год выпуска',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre',
        related_name='titles',
        verbose_name='Жанры'
    )

    class Meta:
        ordering = ('-year', 'name')
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(year__gte=0),
                name='year_positive',
            )
        ]

    def __str__(self) -> str:
        return self.name


class TitleGenre(models.Model):
    """Промежуточная модель для связи Title и Genre."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='genre_relations'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='title_relations'
    )

    class Meta:
        verbose_name = 'Связь произведения и жанра'
        verbose_name_plural = 'Связи произведения и жанров'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'genre'),
                name='unique_title_genre',
            )
        ]

    def __str__(self) -> str:
        return f'{self.title} — {self.genre}'

class Review(models.Model):
    """Модель отзыва на произведение."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message='Оценка должна быть не меньше 1'),
            MaxValueValidator(10, message='Оценка должна быть не больше 10')
        ],
        verbose_name='Оценка произведения'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации отзыва'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review'
            )
        ]

    def __str__(self):
        return f'{self.title} - {self.author}'


class Comment(models.Model):
    """Модель комментария к отзыву."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации комментария'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return f'Комментарий от {self.author} к отзыву {self.review}'
