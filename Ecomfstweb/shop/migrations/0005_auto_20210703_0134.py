# Generated by Django 3.1.4 on 2021-07-03 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_orders'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('items_json', models.CharField(max_length=50000)),
                ('name', models.CharField(max_length=80)),
                ('email', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('zip_code', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=10)),
            ],
        ),
        migrations.DeleteModel(
            name='Orders',
        ),
    ]
