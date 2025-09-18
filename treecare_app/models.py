from django.db import models

# Create your models here.
class Tree(models.Model):
    UploadImage = models.ImageField(upload_to='tree_images/', max_length=255)
    Result = models.CharField(max_length=255)
    Species = models.CharField(max_length=100, blank=True, null=True)
    Disease = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.Result
