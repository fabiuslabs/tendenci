# Generated by Django 3.2.11 on 2022-03-09 12:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0007_auto_20200902_1545'),
        ('jobs', '0002_auto_20170910_1701'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='header_image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='files.file'),
        ),
    ]
