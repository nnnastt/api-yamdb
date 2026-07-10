from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.routers import NestedRouter
from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet,
    get_confirmation_code,
    get_token,
)

API_VERSION = 'v1'

router_v1 = DefaultRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('users', UserViewSet, basename='users')

titles_router = NestedRouter()
titles_router.register(
    r'reviews',
    ReviewViewSet,
    basename='reviews',
    parent_prefix=r'titles/(?P<title_id>[^/.]+)'
)

reviews_router = NestedRouter()
reviews_router.register(
    r'comments',
    CommentViewSet,
    basename='comments',
    parent_prefix=r'titles/(?P<title_id>[^/.]+)/reviews/(?P<review_id>[^/.]+)'
)

auth_urls = [
    path('signup/', get_confirmation_code, name='signup'),
    path('token/', get_token, name='token'),
]

urlpatterns = [
    re_path(rf'^{API_VERSION}/', include(router_v1.urls)),

    path(f'{API_VERSION}/auth/', include(auth_urls)),

    re_path(rf'^{API_VERSION}/', include(titles_router.urls)),

    re_path(rf'^{API_VERSION}/', include(reviews_router.urls)),
]
