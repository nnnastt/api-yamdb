from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, TitleViewSet, get_confirmation_code,
                       get_token)

router_v1 = DefaultRouter()
router_v1.register(r'categories', CategoryViewSet, basename='categories')
router_v1.register(r'genres', GenreViewSet, basename='genres')
router_v1.register(r'titles', TitleViewSet, basename='titles')

urlpatterns = [
    re_path(r'^v1/', include(router_v1.urls)),
    path('v1/auth/signup/', get_confirmation_code, name='signup'),
    path('v1/auth/token/', get_token, name='token'),
    path(
        'v1/titles/<int:title_id>/reviews/',
        ReviewViewSet.as_view({
            'get': 'list',
            'post': 'create'
        })
    ),

    path(
        'v1/titles/<int:title_id>/reviews/<int:pk>/',
        ReviewViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy'
        })
    ),

    path(
        'v1/titles/<int:title_id>/reviews/<int:review_id>/comments/',
        CommentViewSet.as_view({
            'get': 'list',
            'post': 'create'
        })
    ),

    path(
        'v1/titles/<int:title_id>/reviews/<int:review_id>/comments/<int:pk>/',
        CommentViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy'
        })
    ),
]
