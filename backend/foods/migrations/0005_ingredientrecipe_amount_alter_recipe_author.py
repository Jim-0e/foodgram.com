# Generated by Django 4.1.3 on 2024-05-25 06:01

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foods', '0004_rename_tag_name_tagrecipe_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
