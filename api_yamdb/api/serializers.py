from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField

from reviews.constants import (
    CURRENT_YEAR,
    MAX_USERNAME_LENGTH,
    MAX_EMAIL_LENGTH,
    MAX_NAME_LENGTH,
    MIN_YEAR,
    MIN_SCORE,
    MAX_SCORE,
    RESERVED_USERNAME,
    USERNAME_PATTERN,
)
from reviews.models import Category, Comment, CustomUser, Genre, Review, Title


class RegistrationSerializer(serializers.Serializer):
    """Сериализатор для регистрации."""

    email = serializers.EmailField(max_length=MAX_EMAIL_LENGTH, required=True)
    username = serializers.RegexField(
        regex=USERNAME_PATTERN,
        max_length=MAX_USERNAME_LENGTH,
        required=True
    )

    def validate_username(self, username: str) -> str:
        if username.lower() == RESERVED_USERNAME:
            raise ValidationError(
                {'detail': f'Имя пользователя "{RESERVED_USERNAME}" запрещено.'},
                status.HTTP_400_BAD_REQUEST
            )
        return username

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        user_by_username = CustomUser.objects.filter(username=username).first()
        if user_by_username:
            if user_by_username.email != email:
                raise ValidationError(
                    {'detail': 'Пользователь с таким username уже существует.'},
                    status.HTTP_400_BAD_REQUEST
                )
            return data

        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(
                {'detail': 'Пользователь с таким email уже существует.'},
                status.HTTP_400_BAD_REQUEST
            )

        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя (используется и для админа, и для self)."""

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'bio', 'role'
        )
        read_only_fields = ('role',)

    def validate_username(self, value):
        if value == RESERVED_USERNAME:
            raise serializers.ValidationError(
                f'Имя пользователя "{RESERVED_USERNAME}" запрещено.'
            )
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            if self.instance and self.instance.email == value:
                return value
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )
        return value


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    confirmation_code = serializers.CharField(required=True)
    username = serializers.CharField(max_length=MAX_USERNAME_LENGTH, required=True)

    def validate_username(self, username: str) -> str:
        get_object_or_404(CustomUser, username=username)
        return username


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения произведения (GET).

    Включает рейтинг (аннотация из отзывов).
    """

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year',
            'description', 'genre', 'category', 'rating'
        )


class TitleCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания/обновления произведения (POST/PATCH).
    Принимает slug категории и список slug жанров.
    """

    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )
    year = serializers.IntegerField(
        validators=[
            MinValueValidator(
                MIN_YEAR,
                message='Год не может быть меньше -5000'
            ),
            MaxValueValidator(
                CURRENT_YEAR,
                message='Год не может быть больше текущего'
            )
        ]
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def to_representation(self, instance):
        """При GET-запросе используем TitleReadSerializer для полной инфы."""

        return TitleReadSerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs['title_id']

        if (
            request.method == 'POST'
            and Review.objects.filter(
                title_id=title_id,
                author=request.user
            ).exists()
        ):
            raise serializers.ValidationError(
                'Можно оставить только один отзыв.'
            )
        
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
