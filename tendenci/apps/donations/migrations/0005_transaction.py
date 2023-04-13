# Generated by Django 3.2.18 on 2023-03-28 23:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chapters', '0015_remove_chaptermembershipchapterappfield_membership_app'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('donations', '0004_donation_donate_to_entity'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50)),
                ('donation_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('donation_method', models.CharField(choices=[('donorbox', 'Donorbox'), ('hubspot', 'Hubspot')], max_length=50)),
                ('donation_dt', models.DateTimeField(blank=True, null=True)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('donate_to_chapter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='chapters.chapter')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
            },
        ),
    ]
