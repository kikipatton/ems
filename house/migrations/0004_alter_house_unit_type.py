# Generated by Django 5.1.3 on 2024-11-14 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('house', '0003_alter_house_handover_alter_house_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='house',
            name='unit_type',
            field=models.CharField(choices=[('2BR', '2 Bedroom'), ('3BR', '3 Bedroom')], max_length=10, verbose_name='Unit Type'),
        ),
    ]