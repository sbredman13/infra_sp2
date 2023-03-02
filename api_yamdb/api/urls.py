from rest_framework.routers import DefaultRouter
from django.urls import include, path

from api.views import (
    TitlesViewSet,
    CategoriesViewSet,
    GenresViewSet,
    UserViewSet,
    CommentsViewSet,
    ReviewsViewSet,
    generate_confirmation_code,
    get_tokens_for_user,
)


router_v1 = DefaultRouter()

router_v1.register(
    r'titles', TitlesViewSet, basename='titles')
router_v1.register(
    r'categories', CategoriesViewSet,
    basename='categories')
router_v1.register(
    r'genres', GenresViewSet,
    basename='genres')
router_v1.register(
    r'titles/(?P<titles_id>[1-9]\d*)/reviews',
    ReviewsViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>[1-9]\d*)/reviews/(?P<reviews_id>[1-9]\d*)/comments',
    CommentsViewSet, basename='comments'
)
router_v1.register('users', UserViewSet)

urlpatterns = [
    path('v1/auth/signup/', generate_confirmation_code),
    path('v1/auth/token/', get_tokens_for_user),
    path('v1/', include(router_v1.urls)),
]
