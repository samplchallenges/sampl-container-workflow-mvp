# Generated by Django 3.2.3 on 2021-06-04 19:53

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_score_scoretype'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvaluationScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('value', models.FloatField()),
                ('evaluation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='core.evaluation')),
                ('score_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.scoretype')),
            ],
            options={
                'unique_together': {('evaluation', 'score_type')},
            },
        ),
        migrations.CreateModel(
            name='SubmissionRunScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('value', models.FloatField()),
                ('score_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.scoretype')),
                ('submission_run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='core.submissionrun')),
            ],
            options={
                'unique_together': {('submission_run', 'score_type')},
            },
        ),
        migrations.DeleteModel(
            name='Score',
        ),
    ]
