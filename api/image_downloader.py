import imghdr
from io import BytesIO
from multiprocessing import Process

import requests

import rfc3987

from django import db
from django.core.files.images import ImageFile
from django.utils.crypto import get_random_string


from api.models import Image
from api.utils import csv_reader

RANDOM_FILENAME_LENGTH = 16


class ImageDownloader(Process):
    """Download images in a exteranl process."""
    def __init__(self, csv_file, charset):
        self.csv_file = csv_file
        self.charset = charset
        super().__init__()

    def run(self):
        # Close connections to database, to prevent problems.
        db.connections.close_all()
        for row in csv_reader(self.csv_file, self.charset):
            print('reading row {}'.format(row))
            for value in row:
                # Skip already saved files.
                if Image.objects.filter(original_url__iexact=value):
                    print('Already saved')
                    continue
                image_file, image_type = download_image(value)
                if image_file is None:
                    print('not an image')
                    continue
                random_string = get_random_string(RANDOM_FILENAME_LENGTH)
                print('saving image')
                # Create database image object and save it.
                image = Image(original_url=value, type=image_type)

                # http://www.revsys.com/blog/2014/dec/03/loading-django-files-from-code/
                image.original_file.save(
                    '{}.original.{}'.format(random_string, image_type),
                    image_file, save=True
                )
                print('saved image {}'.format(value))
        print('Done with upload')


def download_image(url):
    # Skip empty strings and strings that are not absolute urls.
    if not url or not rfc3987.match(url, 'absolute_URI'):
        return None, None
    # Get url.
    # TODO timeout checks.
    response = requests.get(url)
    if response.status_code == 200:
        image = BytesIO(response.content)
        # Check that the file is really an image.
        image_type = imghdr.what(image)
        if image_type:
            print('got image {}'.format(url))
            return ImageFile(image), image_type
    return None, None
