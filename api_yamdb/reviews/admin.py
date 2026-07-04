from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from reviews.models import (
    Category, CustomUser, Comment,
    Genre, Review, Title, TitleGenre
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Fields', {'fields': ('role',)}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для модели Category."""

    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Админка для модели Genre."""

    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Админка для модели Title."""

    list_display = ('id', 'name', 'year', 'category')
    list_filter = ('category', 'year')
    search_fields = ('name', 'description')

    def get_genres(self, obj):
        """Возвращает список жанров для отображения в списке."""

        return ", ".join([genre.name for genre in obj.genre.all()])

    get_genres.short_description = 'Жанры'


@admin.register(TitleGenre)
class TitleGenreAdmin(admin.ModelAdmin):
    """Админка для промежуточной модели TitleGenre."""

    list_display = ('id', 'title', 'genre')
    list_filter = ('title', 'genre')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админка для модели Review."""
    list_display = ('id', 'title', 'author', 'score', 'pub_date')
    list_filter = ('score', 'pub_date')
    search_fields = ('text', 'author__username', 'title__name')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админка для модели Comment."""
    list_display = ('id', 'review', 'author', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('text', 'author__username')
