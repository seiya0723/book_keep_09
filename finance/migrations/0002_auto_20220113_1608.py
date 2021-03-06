# Generated by Django 3.2.7 on 2022-01-13 07:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.category', verbose_name='カテゴリ'),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together={('name', 'income', 'user')},
        ),
    ]
