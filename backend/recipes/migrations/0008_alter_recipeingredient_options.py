# Generated by Django 4.2.2 on 2023-07-02 14:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_alter_recipe_users_favorite_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'verbose_name': 'Ингредиент для рецепта', 'verbose_name_plural': 'Ингредиенты для рецептов'},
        ),
    ]
