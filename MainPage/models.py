from django.db import models

# Create your models here.

class Notes(models.Model):
    content = models.TextField()

class Pages(models.Model):
    name = models.TextField()
    url = models.TextField()