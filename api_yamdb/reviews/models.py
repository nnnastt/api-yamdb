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
