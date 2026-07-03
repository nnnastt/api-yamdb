from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Genre, Title, Review, Comment


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


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        request = self.context['request']
        view = self.context['view']
        title_id = view.kwargs.get('title_id')

        if request.method == 'POST':
            if Review.objects.filter(
                title_id=title_id,
                author=request.user
            ).exists():
                raise serializers.ValidationError(
                    'Можно оставить только один отзыв'
                )
        return data 


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
