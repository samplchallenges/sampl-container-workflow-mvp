# Generated by Django 3.2.7 on 2021-10-31 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20210927_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='notes',
            field=models.TextField(blank=True, help_text='Submission Annotations and Notes-to-self.\nPlease place any extra notes or annotations about your submission or submission run here. This section is only intended for notes-to-self, and will be disregarded by challenge administrators.\nUnlike other sections, you may modify this section after the challenge has concluded.\n', null=True),
        ),
    ]