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
        for model in MODELS:
            if model.objects.exists():
                print(model, ' data already loaded....')
                print("Deleting data")
                model.objects.all().delete()
                print("Data is deleted")
        print("Loading data")
        for file, model in zip(FILES, MODELS):
            import_csv(f'static/data/{file}', model)
