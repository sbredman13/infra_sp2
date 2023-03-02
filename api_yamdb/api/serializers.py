import datetime as dt

from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comments, Genre, Review, Title, User


class CategoriesSerializer(serializers.ModelSerializer):
    '''Сериализатор для отображения Категорий'''

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenresSerializer(serializers.ModelSerializer):
    '''Сериализатор для отображения Жанров'''

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitlesSerializer(serializers.ModelSerializer):
    '''Сериализатор для создания произведения
    с функцией валидации, которая не позволяет создать произведения
    если они вышли в будущем времени'''
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )

    def validate_year(self, value):
        year = dt.date.today().year
        if value > year:
            raise serializers.ValidationError(
                'Нельзя добавлять произведения, которые еще не вышли!')
        return value

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category'
        )


class ReadTitleSerializer(serializers.ModelSerializer):
    '''Сериализатор для отображения Произведений'''
    rating = serializers.IntegerField(read_only=True)
    genre = GenresSerializer(read_only=True, many=True)
    category = CategoriesSerializer(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category', 'rating',)


class ReviewsSerializer(serializers.ModelSerializer):
    '''Сериализатор для Ревью. Реализована функция,
    которая не позволяет одному автору написать 2 ревью.'''
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    def validate(self, value):
        author = self.context['request'].user
        title_id = (self.context['request'].
                    parser_context['kwargs'].get('titles_id'))
        if self.context['request'].method == 'POST':
            title = get_object_or_404(Title, id=title_id)
            if title.reviews.filter(author=author).exists():
                raise serializers.ValidationError(
                    'Вы не можете написать два отзыва на одно произведение'
                )
        return value

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ('title',)


class CommentsSerializer(serializers.ModelSerializer):
    '''Сериализатор для Комментариев'''
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comments
        fields = ('id', 'text', 'pub_date', 'review', 'author',)
        read_only_fields = ('review',)


class UserSerializer(serializers.ModelSerializer):
    '''Сериализатор кастомного класса Пользователя'''

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role')


class SignupSerializer(serializers.Serializer):
    '''Сериализатор для Регистрации'''
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    def validate(self, data):
        email = data['email']
        username = data['username']
        is_user_exists = User.objects.filter(username=username).exists()
        email_exists = User.objects.filter(email=email).exists()
        if username == 'me':
            raise serializers.ValidationError(
                'Зарпещено создавать пользователя с таким именем!'
            )
        if is_user_exists and not email_exists:
            raise serializers.ValidationError(
                'Пользователь с таким именем уже существует.'
            )
        if not is_user_exists and email_exists:
            raise serializers.ValidationError(
                'Такой почтовый адресс уже существует.'
            )
        return data


class TokenSerializer(serializers.Serializer):
    '''Сериализатор для Токена'''
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=200)

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        confirmation_code = data['confirmation_code']
        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError('Недействительный код!')
        return data
