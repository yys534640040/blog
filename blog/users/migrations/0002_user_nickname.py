# Generated by Django 3.0.5 on 2020-07-10 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='nickname',
            field=models.CharField(default='', max_length=20, verbose_name='昵称'),
        ),
    ]
