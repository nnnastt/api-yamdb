from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilter
from api.permissions import (IsAdminOrReadOnly, IsAdminUser,
                             IsAuthorModeratorAdminOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, RegistrationSerializer,
                             ReviewSerializer, TitleCreateSerializer,
                             TitleReadSerializer, TokenSerializer,
                             UserSerializer)
from reviews.models import Category, Genre, Review, Title, User


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления пользователями."""

    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    lookup_field = 'username'
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me',
        url_name='me'
    )
    def me(self, request):
        """Профиль текущего пользователя."""

        user = request.user
        serializer = UserSerializer(user)

        if request.method == 'PATCH':
            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)

        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request) -> Response:
    """Получение JWT токена."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    user = User.objects.get(username=username)
    token = RefreshToken.for_user(user)
    return Response(
        {'token': str(token.access_token)},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def get_confirmation_code(request) -> Response:
    """Получение кода подтверждения."""
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']
    username = serializer.validated_data['username']
    user, _ = User.objects.get_or_create(
        username=username,
        email=email
    )
    user.send_mail()
    return Response(serializer.data, status=status.HTTP_200_OK)


class BaseCategoryGenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый вьюсет для Category и Genre."""

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'delete']


class CategoryViewSet(BaseCategoryGenreViewSet):
    """Вьюсет для модели Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseCategoryGenreViewSet):
    """Вьюсет для модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели Title.

    GET — доступно всем, остальное — только администратору.
    """

    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).order_by('id')
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
    """Вьюсет для отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorModeratorAdminOrReadOnly,
    )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        return get_object_or_404(
            Title,
            pk=self.kwargs['title_id']
        )

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев."""

    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorModeratorAdminOrReadOnly,
    )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs['review_id'],
            title_id=self.kwargs['title_id']
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )
