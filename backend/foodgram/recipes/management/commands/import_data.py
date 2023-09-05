import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import data from CSV file'

    def handle(self, *args, **kwargs):
        csv_file = '/Users/Maria/Dev/foodgram-project-react/data/ingredients.csv'
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                name, measurement_unit = row
                Ingredient.objects.create(
                    name=name,
                    measurement_unit=measurement_unit
                )
                self.stdout.write(self.style.SUCCESS('Successfully imported data'))
