from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, TitleViewSet, UserViewSet,
                       get_confirmation_code, get_token)

API_VERSION = 'v1'

router_v1 = DefaultRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    re_path(rf'^{API_VERSION}/', include(router_v1.urls)),

    path(f'{API_VERSION}/auth/signup/', get_confirmation_code),
    path(f'{API_VERSION}/auth/token/', get_token),

    path(
        f'{API_VERSION}/titles/<int:title_id>/reviews/',
        ReviewViewSet.as_view({
            'get': 'list',
            'post': 'create',
        }),
        name='reviews-list',
    ),

    path(
        f'{API_VERSION}/titles/<int:title_id>/reviews/<int:pk>/',
        ReviewViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='reviews-detail',
    ),

    path(
        f'{API_VERSION}/titles/<int:title_id>/reviews/'
        f'<int:review_id>/comments/',
        CommentViewSet.as_view({
            'get': 'list',
            'post': 'create',
        }),
        name='comments-list',
    ),

    path(
        f'{API_VERSION}/titles/<int:title_id>/reviews/'
        f'<int:review_id>/comments/<int:pk>/',
        CommentViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='comments-detail',
    ),
]
