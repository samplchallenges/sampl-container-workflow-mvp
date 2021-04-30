# Generated by Django 3.2 on 2021-04-08 18:23

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_scoremaker'),
    ]

    operations = [
        migrations.CreateModel(
            name='InputElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('is_public', models.BooleanField(default=False)),
                ('challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.challenge')),
            ],
            options={
                'unique_together': {('challenge', 'name')},
            },
        ),
        migrations.CreateModel(
            name='InputType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('key', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.challenge')),
            ],
            options={
                'unique_together': {('challenge', 'key')},
            },
        ),
        migrations.CreateModel(
            name='InputValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('value', models.TextField()),
                ('input_element', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.inputelement')),
                ('input_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.inputtype')),
            ],
            options={
                'unique_together': {('input_element', 'input_type')},
            },
        ),
    ]