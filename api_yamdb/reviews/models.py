from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models
from django.db.models import Avg, UniqueConstraint

from reviews.validators import my_year_validator


class User(AbstractUser):
    '''Кастомная модель пользователя'''
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    username = models.CharField(
        unique=True,
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Недопустимые символы в имени',
            )
        ]
    )
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, blank=True)
    last_login = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=10,
        choices=[
            (USER, 'Пользователь'),
            (MODERATOR, 'Модератор'),
            (ADMIN, 'Администратор')
        ],
        default=USER,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == (
            self.MODERATOR
            or self.is_superuser
            or self.is_staff
        )

    @property
    def is_user(self):
        return self.role == self.USER


class Category(models.Model):
    '''Модель Категории'''
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.slug


class Genre(models.Model):
    '''Модель Жанра'''
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.slug


class Title(models.Model):
    '''Модель Произведения'''
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='title')
    genre = models.ManyToManyField(
        Genre, related_name='title')
    name = models.CharField(max_length=256)
    year = models.IntegerField(validators=[my_year_validator])
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Тайтл'
        verbose_name_plural = 'Тайтлы'

    def __str__(self):
        return self.name

    @property
    def average_score(self):
        if hasattr(self, '_average_score'):
            return self._average_score
        return self.reviews.aggregate(Avg('score'))


class Review(models.Model):
    '''Модель Ревью'''
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    score = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации отзыва',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')

    class Meta:
        constraints = [
            UniqueConstraint(fields=['author', 'title'], name='unique_names')
        ]
        verbose_name = 'Обзор'
        verbose_name_plural = 'Обзоры'

    def __str__(self):
        return self.title


class Comments(models.Model):
    '''Модель Комментариев'''
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'

    def __str__(self):
        return self.text
