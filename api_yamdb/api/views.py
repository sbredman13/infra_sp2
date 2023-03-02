from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, status, filters, mixins
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend


from api.permissions import (
    IsAdminForUsers,
    IsAdminModeratorAuthorOrReadOnly,
    IsAdmin
)
from reviews.models import Title, Category, Genre, User, Review
from api.serializers import (
    TitlesSerializer,
    ReadTitleSerializer,
    CategoriesSerializer,
    GenresSerializer,
    SignupSerializer,
    UserSerializer,
    TokenSerializer,
    CommentsSerializer,
    ReviewsSerializer,
)
from api.filters import TitlesFilter
from api_yamdb.settings import EMAIL_FROM


class TitlesViewSet(viewsets.ModelViewSet):
    '''Создание и отображение Произведений'''
    queryset = Title.objects.annotate(rating=Avg('reviews__score')).all()
    serializer_class = TitlesSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter
    permission_classes = (IsAdmin,)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TitlesSerializer
        return ReadTitleSerializer


class CategoriesAndGenresViewset(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    '''Админский класс для создания категорий и жанров'''

    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoriesViewSet(CategoriesAndGenresViewset):
    '''Получение списка Категорий'''
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class GenresViewSet(CategoriesAndGenresViewset):
    '''Получение списка Жанров'''
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    '''Получение и создание Ревью'''
    serializer_class = ReviewsSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminModeratorAuthorOrReadOnly,
    )

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs['titles_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Title, pk=self.kwargs['titles_id'])
        serializer.save(author=self.request.user, title=review)


class CommentsViewSet(viewsets.ModelViewSet):
    '''Получение и создание Комментариев'''
    serializer_class = CommentsSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminModeratorAuthorOrReadOnly,
    )
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs['reviews_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['reviews_id'])
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    '''Получение списка пользователей информации о себе.
    Доступ к редактированию информации о пользователях.'''
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminForUsers,)
    lookup_field = 'username'

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(role=request.user.role)
            return Response(serializer.data)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_confirmation_code(request):
    '''Генерация кодов и отправка их по почте для получения токенов.'''
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user, _ = User.objects.get_or_create(
            username=request.data['username'],
            email=request.data['email']
        )
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Welcome',
            f'Your code --> {confirmation_code}',
            EMAIL_FROM,
            [user.email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_tokens_for_user(request):
    '''Получение и валидация токенов для пользователей.'''
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        user = get_object_or_404(User, username=request.data['username'])
        token = AccessToken.for_user(user)
        return Response({'token': str(token)})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
