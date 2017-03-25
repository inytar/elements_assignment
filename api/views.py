import codecs
import csv

from rest_framework import decorators
from rest_framework import mixins
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework import viewsets

# Create your views here.

from api.models import CSV, Image, ResizedImage
from api.renderers import ImageRenderer
from api.serializers import CSVSerializer, ImageSerializer


class CSVViewSet(mixins.CreateModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    queryset = CSV.objects.all()
    serializer_class = CSVSerializer

    def retrieve(self, request, *args, **kwargs):
        """Add the csv rows to the return value."""
        csv_object = self.get_object()

        # Add image if it it exists.
        serializer = self.get_serializer(csv_object)
        data = serializer.data
        data['rows'] = self.get_rows(csv_object)
        return Response(data)

    def get_rows(self, csv_object):
        """An generator the get and format rows in `csv_object`."""
        for i, row in enumerate(csv.reader(
                codecs.iterdecode(csv_object.csv_file,
                                  csv_object.charset)
        )):
            # Skip first row if csv has a header.
            if i == 0 and csv_object.has_header:
                continue
            # TODO escape value.
            yield tuple({'value': v, 'image': self.get_image(v)} for v in row)

    def get_image(self, url):
        """Get image from database."""
        # Don't do a lookup for empty strings.
        if not url:
            return None
        try:
            # TODO We clearly have a performance issue here, we are
            # running a query for every image we want to look up. In
            # a future revision get all images associated with this
            # csv at once, and then search for the correct one in python.
            image = Image.objects.get(original_url__iexact=url)
        except Image.DoesNotExist:
            # No image saved, just return None.
            return None
        # Return the url to the image instance.
        return ImageSerializer(image, context={'request': self.request}).\
            data['url']


class ImageViewSet(mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    renderer_classes = (JSONRenderer, ImageRenderer, BrowsableAPIRenderer)

    def retrieve(self, request, *args, **kwargs):
        """Show image instead of return json."""
        if request.accepted_renderer.format == 'image':
            image = self.get_object()
            size = 'original'
            if size.lower() == 'original':
                img = image
            else:
                try:
                    img = ResizedImage.objects.get(image=image, size=size)
                except ResizedImage.DoesNotExist:
                    img = image.resize(size)

            return Response(img.file, content_type='image/{}'.format(image.type))
        else:
            return super().retrieve(request, *args, **kwargs)
