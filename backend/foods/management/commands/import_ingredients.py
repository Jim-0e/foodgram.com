"""Загрузка данных ингредиентов в таблицу."""

import csv

from django.core.management.base import BaseCommand

from ...models import Ingredients


class Command(BaseCommand):
    """Импорт данных ингредиентов из CSV-файла."""

    help = 'Импорт данных ингредиентов из CSV-файла.'

    def add_arguments(self, parser):
        """Добавление аргумента к команде."""
        parser.add_argument('csv_file',
                            type=str,
                            help='CSV-файл с данными ингредиентов.')

    def handle(self, *args, **options):
        """Функция команды управления Django."""
        csv_file = options['csv_file']

        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                name, measurement_unit = row
                Ingredients.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit)

        self.stdout.write(self.style.SUCCESS(
            'Данные ингредиентов успешно импортированы.'))
