from django.db import models

# Create your models here.
class Blog(models.Model):
    title = models.CharField(max_length=200)
    hostname = models.CharField(max_length=200)
    init= models.BooleanField(default=False)
