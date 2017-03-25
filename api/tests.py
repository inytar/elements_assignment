import os

from django.core.files.images import ImageFile
from django.test import TestCase

import requests

import requests_mock

# Create your tests here.

from api import image_downloader


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


class TestCsvView(TestCase):
    pass
