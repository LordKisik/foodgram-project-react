import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag


def get_reader(file_name):
    csv_path = os.path.join(settings.BASE_DIR, 'static/data/', file_name)
    csv_file = open(csv_path, 'r', encoding='utf-8')
    return csv.reader(csv_file, delimiter=',')


class Command(BaseCommand):
    help = 'Импорт ингредиентов из csv-файла'

    def handle(self, *args, **options):
        csv_reader = get_reader('ingredients.csv')
        try:
            for row in csv_reader:
                name, measurement_unit = row[0], row[1]
                obj, created = Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Файл {csv_reader} не найден"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
        else:
            self.stdout.write(self.style.SUCCESS('Ингредиенты добавлены.'))

        csv_reader = get_reader('tags.csv')
        try:
            for row in csv_reader:
                name, color, slug = row[0], row[1], row[2]
                obj, created = Tag.objects.get_or_create(
                    name=name, color=color, slug=slug)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Файл {csv_reader} не найден"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
        else:
            self.stdout.write(self.style.SUCCESS('Теги добавлены.'))
