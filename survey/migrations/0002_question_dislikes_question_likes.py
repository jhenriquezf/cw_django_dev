# Generated by Django 4.2.7 on 2023-11-23 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='dislikes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='question',
            name='likes',
            field=models.IntegerField(default=0),
        ),
    ]