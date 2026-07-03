from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.pagination import PageNumberPagination

from reviews.models import Category, Genre, Title
from api.permissions import IsAdminOrReadOnly
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleCreateSerializer,
    TitleReadSerializer,
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
