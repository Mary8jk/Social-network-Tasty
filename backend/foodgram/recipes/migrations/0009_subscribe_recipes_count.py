# Generated by Django 3.2.3 on 2023-10-01 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20230929_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscribe',
            name='recipes_count',
            field=models.IntegerField(default=0),
        ),
    ]