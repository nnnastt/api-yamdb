from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения произведения (GET).
    Включает рейтинг (аннотация из отзывов).
    """

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year',
            'description', 'genre', 'category',
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
            MinValueValidator(0),
            MaxValueValidator(2026),
        ]
    )

    name = serializers.CharField(max_length=256)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_name(self, value):
        """Дополнительная валидация длины названия."""
        if len(value) > 256:
            raise serializers.ValidationError(
                'Название произведения не может быть длиннее 256 символов.'
            )
        return value

    def to_representation(self, instance):
        """При GET-запросе используем TitleReadSerializer для полной инфы."""

        return TitleReadSerializer(instance).data
