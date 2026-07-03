import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from reviews.models import Category, Genre, Title, TitleGenre


class Command(BaseCommand):
    help = 'Импорт данных из CSV'

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        data_dir = base_dir / 'static' / 'data'

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