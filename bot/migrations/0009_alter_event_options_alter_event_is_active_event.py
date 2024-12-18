# Generated by Django 5.0.6 on 2024-12-01 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0008_remove_event_end_time_alter_event_start_time'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['start_time'], 'verbose_name': 'Событие', 'verbose_name_plural': 'События'},
        ),
        migrations.AlterField(
            model_name='event',
            name='is_active_event',
            field=models.BooleanField(default=False, verbose_name='Статус активного события'),
        ),
    ]
