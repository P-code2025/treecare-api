from django.db import models

# Create your models here.
class Tree(models.Model):
    UploadImage = models.ImageField(upload_to='tree_images/')
    Result = models.CharField(max_length=255)

    def __str__(self):
        return self.Result
        