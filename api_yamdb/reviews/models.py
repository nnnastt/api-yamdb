import datetime
import random

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.constants import (CODE_SYMBOLS_NUMBER, CODE_VALIDITY_PERIOD,
                               MAX_ROLE_LENGTH, MAX_SCORE, MIN_SCORE,
                               MODELS_MAX_LENGTH, RESERVED_USERNAME)
from reviews.core.models import NameSlugModel, PublishedModel


def validate_not_me(value):
    """Валидатор, запрещающий использование username 'me'."""
    if value == RESERVED_USERNAME:
        raise models.ValidationError(
            f'Имя пользователя "{RESERVED_USERNAME}" запрещено.'
        )


def get_current_year():
    """Возвращает текущий год."""
    return datetime.datetime.now().year


class UserRole(models.TextChoices):
    """Роли пользователя."""

    USER = 'user', 'Пользователь'
    MODERATOR = 'moderator', 'Модератор'
    ADMIN = 'admin', 'Администратор'


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта',
    )
    role = models.CharField(
        max_length=MAX_ROLE_LENGTH,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name='Роль',
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='Биография',
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_moderator(self) -> bool:
        return self.role == UserRole.MODERATOR or self.is_admin

    def generate_code(self) -> str:
        confirmation_code = ''.join(
            str(random.randint(0, 9)) for _ in range(CODE_SYMBOLS_NUMBER)
        )
        cache.set(
            self.username,
            confirmation_code,
            timeout=CODE_VALIDITY_PERIOD
        )
        return confirmation_code

    def code_is_valid(self, user_code: str) -> bool:
        correct_code = cache.get(self.username)
        if user_code == correct_code:
            return True
        return False

    def send_mail(self) -> None:
        confirmation_code = self.generate_code()
        send_mail(
            subject='Код подтверждения',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email],
            fail_silently=True,
        )


class Category(NameSlugModel):
    """Модель категории произведения."""

    class Meta(NameSlugModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(NameSlugModel):
    """Модель жанра произведения."""

    class Meta(NameSlugModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(
        max_length=MODELS_MAX_LENGTH,
        verbose_name='Название произведения'
    )
    year = models.SmallIntegerField(
        validators=[
            MaxValueValidator(
                get_current_year,
                message='Год не может быть больше текущего'
            )
        ],
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

    def __str__(self) -> str:
        return self.name


class TitleGenre(models.Model):
    """Промежуточная модель для связи Title и Genre."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='titles'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='genres'
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


class Review(PublishedModel):
    """Модель отзыва на произведение."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )

    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                MIN_SCORE,
                message=f'Оценка должна быть не меньше {MIN_SCORE}'
            ),
            MaxValueValidator(
                MAX_SCORE,
                message=f'Оценка должна быть не больше {MAX_SCORE}'
            )
        ],
        verbose_name='Оценка произведения'
    )

    class Meta:
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


class Comment(PublishedModel):
    """Модель комментария к отзыву."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta(PublishedModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
