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

reviews_router = DefaultRouter()
reviews_router.register('reviews', ReviewViewSet, basename='reviews')

comments_router = DefaultRouter()
comments_router.register('comments', CommentViewSet, basename='comments')

urlpatterns = [
    re_path(rf'^{API_VERSION}/', include(router_v1.urls)),
    path(f'{API_VERSION}/auth/signup/', get_confirmation_code, name='signup'),
    path(f'{API_VERSION}/auth/token/', get_token, name='token'),
    re_path(
        rf'^{API_VERSION}/titles/(?P<title_id>\d+)/reviews/',
        include(reviews_router.urls)
    ),
    re_path(
        rf'^{API_VERSION}/titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments/',
        include(comments_router.urls)
    ),
]
