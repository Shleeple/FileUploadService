from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    document_file = models.FileField(upload_to='documents/', max_length=255)
    isd = models.CharField(max_length=255)
    word_count = models.IntegerField()
    document_type = models.CharField(max_length=255)
    unique_id = models.CharField(max_length=255, unique=True)
