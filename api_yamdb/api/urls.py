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

auth_urls = [
    path('signup/', get_confirmation_code, name='signup'),
    path('token/', get_token, name='token'),
]

reviews_urlpatterns = [
    re_path(
        r'^$',
        ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='review-list'
    ),
    re_path(
        r'^(?P<pk>\d+)/$',
        ReviewViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy'
        }),
        name='review-detail'
    ),
]

comments_urlpatterns = [
    re_path(
        r'^$',
        CommentViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='comment-list'
    ),
    re_path(
        r'^(?P<pk>\d+)/$',
        CommentViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy'
        }),
        name='comment-detail'
    ),
]

urlpatterns = [
    re_path(rf'^{API_VERSION}/', include(router_v1.urls)),

    path(f'{API_VERSION}/auth/', include(auth_urls)),

    re_path(
        rf'^{API_VERSION}/titles/(?P<title_id>\d+)/reviews/',
        include(reviews_urlpatterns)
    ),

    re_path(
        rf'^{API_VERSION}/titles/(?P<title_id>\d+)/reviews/'
        r'(?P<review_id>\d+)/comments/',
        include(comments_urlpatterns)
    ),
]
