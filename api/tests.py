import os
from unittest.mock import patch
from urllib.parse import urlparse

from django.core.files.images import ImageFile
from django.test import TestCase
from django.urls import reverse

from rest_framework import status

import requests

import requests_mock

# Create your tests here.

from elements_csv import settings
from api import image_downloader
from api.models import CSV


class TestImageDownloader(TestCase):

    image = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'test_image.jpeg')

    @requests_mock.Mocker()
    def test_download_image(self, m):
        # Test cases with url an expected result.
        test_cases = [
            ('not_an_url', (object, None)),
            ('', (object, None)),
            (None, (object, None)),
            ('http://example.com/404', (object, None)),
            ('http://example.com/no_image', (object, None)),
            ('http://example.com/time_out', (object, None)),
            ('/not_absolute', (object, None)),
            ('example.com/image', (object, None)),  # not absolute.
            ('/example.com/image', (object, None)),  # not absolute.
            ('http://example.com/image', (ImageFile, 'jpeg')),
            ('http://example.com/redirect', (ImageFile, 'jpeg')),
        ]

        # Register mock urls
        m.get('http://example.com/404', status_code=404)
        m.get('http://example.com/no_image', text='Not an image')
        m.get('http://example.com/time_out',
              exc=requests.exceptions.ConnectTimeout)
        with open(self.image, 'rb') as f:
            m.get('http://example.com/image', content=f.read())
        m.get('http://example.com/redirect', status_code=301,
              headers={'location': 'http://example.com/image'})

        for url, expected in test_cases:
            print(url, expected)
            result = image_downloader.download_image(url)
            self.assertEqual(result[1], expected[1])
            self.assertTrue(isinstance(result[0], expected[0]))

    # TODO Add test for ImageDownloader class.


class TestCSVView(TestCase):

    def _create_test_file(self, path):
        f = open(path, 'w')
        f.write('test123\n')
        f.close()
        f = open(path, 'rb')
        return f

    def test_upload_file_success(self): #, ImageDownloader):
        url = reverse('csv-list')
        data = self._create_test_file('/tmp/test_upload.csv')
        data = {'csv_file': data}

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(urlparse(
            response.data['csv_file']).path.startswith(settings.MEDIA_URL))
        # Test that CSV is in database.
        CSV.objects.get(pk=response.data['id'])

    def test_upload_file_bad_extension(self, ImageDownloader):
        url = reverse('csv-list')
        data = self._create_test_file('/tmp/test_upload.html')
        data = {'csv_file': data}

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(ImageDownloader.called)

    # def test_upload_file_not_parsable(self):
    #     url = reverse('csv-list')
    #     data = self._create_test_file('/tmp/test_upload.csv')
    #     data = {'csv_file': data}

    #     response = self.client.post(url, data, format='multipart')
    #     self.assertEqual(response.status_code, status.HTTP_400_CREATED)
