# Generated by Django 3.0.6 on 2020-06-04 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
