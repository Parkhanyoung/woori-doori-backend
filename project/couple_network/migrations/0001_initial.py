# Generated by Django 3.2.9 on 2021-11-12 07:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoupleRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('requestor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='c_request', to='user.profile')),
                ('responsor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='c_response', to='user.profile')),
            ],
        ),
        migrations.CreateModel(
            name='CoupleNet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('members', models.ManyToManyField(related_name='couple_net', to='user.Profile')),
            ],
        ),
    ]
