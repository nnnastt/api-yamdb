import csv

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from reviews.models import (
    Category, Comment, Genre,
    Review, Title, TitleGenre
)
from reviews.constants import DATA_DIR_PATH_FOR_CSV

User = get_user_model()


class Command(BaseCommand):
    help = 'Импорт данных из CSV'

    def handle(self, *args, **options):
        data_dir = DATA_DIR_PATH_FOR_CSV

        with open(data_dir / 'category.csv', 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                Category.objects.get_or_create(
                    slug=row['slug'],
                    defaults={'name': row['name']}
                )

        with open(data_dir / 'genre.csv', 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                Genre.objects.get_or_create(
                    slug=row['slug'],
                    defaults={'name': row['name']}
                )

        with open(data_dir / 'titles.csv', 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                category = Category.objects.get(id=row['category'])
                Title.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'year': row['year'],
                        'category': category,
                        'description': '',
                    }
                )

        with open(data_dir / 'genre_title.csv', 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                TitleGenre.objects.get_or_create(
                    title=title,
                    genre=genre
                )

        with open(data_dir / 'users.csv', 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                User.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'username': row['username'],
                        'email': row['email'],
                        'role': row.get('role', 'user'),
                        'first_name': row.get('first_name', ''),
                        'last_name': row.get('last_name', ''),
                    }
                )

        with open(data_dir / 'review.csv', 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                title = Title.objects.get(id=row['title_id'])
                author = User.objects.get(id=row['author'])
                Review.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'title': title,
                        'text': row['text'],
                        'author': author,
                        'score': row['score'],
                        'pub_date': row['pub_date'],
                    }
                )

        with open(data_dir / 'comments.csv', 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                review = Review.objects.get(id=row['review_id'])
                author = User.objects.get(id=row['author'])
                Comment.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'review': review,
                        'text': row['text'],
                        'author': author,
                        'pub_date': row['pub_date'],
                    }
                )
