# Generated by Django 4.2.2 on 2023-07-01 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='favorite_recipes',
            new_name='favorites',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='shopping_cart',
            new_name='users_shopping_carts',
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(db_index=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(db_index=True, to='recipes.tag'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(db_index=True, max_length=32),
        ),
    ]