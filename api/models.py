from django.contrib.postgres import fields as pgfields
from django.db import models

# Create your models here.


class CSV(models.Model):
    name = models.CharField(max_length=100)
    charset = models.CharField(max_length=10)
    uploaded = models.DateTimeField(auto_now_add=True)
    has_header = models.BooleanField(default=True)
    # A list of the csvs headers. can be set by the user, or determined
    # from the file headers.
    header = pgfields.ArrayField(models.CharField(max_length=20))
    csv_file = models.FileField(upload_to='api/csvs/')

    class Meta:
        ordering = ('-uploaded',)


class Image(models.Model):
    # We are going to search on url often make sure it has a index.
    original_url = models.URLField()
    uploaded = models.DateTimeField(auto_now_add=True)
    original_file = models.ImageField(upload_to='api/images/')
    type = models.CharField(max_length=10)

    class Meta:
        ordering = ('-uploaded',)

    def resize(self, *, x, y):
        return self
        pass


class ResizedImage(models.Model):
    image = models.ForeignKey(Image)
    height = models.CharField(max_length=20)
    file = models.ImageField(upload_to='api/images/')
