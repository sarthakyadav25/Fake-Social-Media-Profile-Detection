# Generated by Django 5.0.4 on 2024-04-17 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_alter_profile_profile_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='fake',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
        ),
    ]