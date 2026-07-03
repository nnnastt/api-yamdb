from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import MethodNotAllowed


from reviews.models import Category, Genre, Title, Review, Comment

from api.permissions import (
    IsAdminOrReadOnly,
    IsAuthorModeratorAdminOrReadOnly
)

from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleCreateSerializer,
    TitleReadSerializer,
    ReviewSerializer,
    CommentSerializer,
)

from api.filters import TitleFilter


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'delete']  # Временное решение для прохождения моих тестов(так же напомните)

    def retrieve(self, request, *args, **kwargs):  # это тоже
        raise MethodNotAllowed('GET')

class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'delete']  # Временное решение для прохождения моих тестов(так же напомните)

    def retrieve(self, request, *args, **kwargs):  # это тоже
        raise MethodNotAllowed('GET')

class TitleViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели Title.
    GET — доступно всем, остальное — только администратору.
    """

    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = TitleFilter
    search_fields = ('name',)
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от метода запроса."""

        if self.request.method in ('POST', 'PATCH', 'PUT'):
            return TitleCreateSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Review."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )



class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Comment."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs['review_id'])

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )
