# Generated by Django 3.1.4 on 2021-07-13 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20210712_2336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='chead0',
            field=models.TextField(default='', max_length=5000),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='chead1',
            field=models.TextField(default='', max_length=5000),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='chead2',
            field=models.TextField(default='', max_length=5000),
        ),
    ]