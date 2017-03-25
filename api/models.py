from contextlib import closing
from io import BytesIO

from django.contrib.postgres import fields as pgfields
from django.db import models

from PIL import Image as PImage

# Create your models here.


class CSV(models.Model):
    """Model of a CSV file.

    Saves the CSV file and the headers of the file.
    """
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


image_sizes = {'thumbnail': 128,
               'small': 512,
               'medium': 1024,
               'large': 4096,
               'original': None}


class Image(models.Model):
    """Model of the original image."""
    # TODO We are going to search on url often make sure it has a index. Also
    # add a unique and lower to this column, as we should only have one
    # image per link.
    source = models.URLField()
    uploaded = models.DateTimeField(auto_now_add=True)
    file = models.ImageField(upload_to='api/images/')
    type = models.CharField(max_length=10)

    class Meta:
        ordering = ('-uploaded',)

    def resize(self, size):
        """Resize the image to `size`."""
        width = image_sizes[size]
        # Open file for usage.
        self.file.open()
        # We only shrink the image, so if width is equal or larger than
        # original file just return self.
        if not width or width >= self.file.width:
            return self
        image_name, _, image_type = self.file.name.rsplit('.', 2)
        with closing(self.file):
            # Resize with pillow.
            image_object = PImage.open(self.file)
            # Size is always width dependent and not height.
            image_object.thumbnail((width, self.file.height))
            image_file = BytesIO()
            image_object.save(image_file, format=image_type)
        # Use the same random string and image type as orignal
        resized = ResizedImage(image=self, size=size)
        resized.file.save('{}.{}.{}'.format(image_name, size, image_type),
                          image_file, save=True)
        return resized


class ResizedImage(models.Model):
    """Model of a rezised image."""
    image = models.ForeignKey(Image)
    size = models.CharField(max_length=20)
    file = models.ImageField(upload_to='api/images/')
