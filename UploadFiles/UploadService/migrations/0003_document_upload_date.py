# Generated by Django 4.2.7 on 2023-11-27 01:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('UploadService', '0002_alter_document_document_file_processeddocument_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='upload_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
