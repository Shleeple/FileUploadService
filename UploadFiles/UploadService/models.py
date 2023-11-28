from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.


class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    document_file = models.FileField(upload_to='documents/', max_length=255)
    isd = models.CharField(max_length=255)
    word_count = models.IntegerField()
    document_type = models.CharField(max_length=255)
    unique_id = models.CharField(max_length=255, unique=True)
    upload_date = models.DateTimeField()

    # foreign key to link to processed document
    processed_document = models.OneToOneField('ProcessedDocument', null=True, blank=True, on_delete=models.SET_NULL, related_name='processed_document')


class ProcessedDocument(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='processed_document_relation')
    processed_document_file = models.FileField(upload_to='processed_documents/', max_length=255)