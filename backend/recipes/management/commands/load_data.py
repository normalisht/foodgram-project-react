import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag

FILES = [
    'ingredients.csv', 'tags.csv'
]
MODELS = [Ingredient, Tag]


def import_csv(file, model):
    with open(file, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        print(file)
        objects = []
        for row in reader:
            objects.append(model(**row))
        model.objects.bulk_create(objects)


class Command(BaseCommand):
    help = "Loads data from somefiles.csv"

    def handle(self, *args, **options):
        for file, model in zip(FILES, MODELS):
            model_name = model._meta.model_name.capitalize()
            if model.objects.exists():
                print(f'{model_name} data already loaded')
            else:
                print(f"Loading data in {model_name}")
                import_csv(f'static/data/{file}', model)
