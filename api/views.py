import codecs
import csv

from django.utils.html import escape

from rest_framework import decorators
from rest_framework import mixins
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

# Create your views here.

from api.models import CSV, Image, image_sizes, ResizedImage
from api.permissions import IsAdminUserOrReadOnly
from api.renderers import ImageRenderer
from api.serializers import CSVSerializer, ImageSerializer


class CSVViewSet(mixins.CreateModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """
    list:
    Return a list of all uploaded CSV files.

    create:
    Upload a new CSV file.

    The `header` parameter gives problems
    when uploading using the Django forms. Using curl does not give this
    problem.

    retrieve:
    Return the given CSV file with all its rows.

    delete:
    Delete the CSV file.
    """
    queryset = CSV.objects.all()
    serializer_class = CSVSerializer
    permission_classes = (IsAdminUserOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
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
            yield tuple({'value': escape(v), 'image': self.get_image(v)} for
                        v in row)

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
            image = Image.objects.get(source__iexact=url)
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

    def metadata(self, request):
        data = super().metadata(request)
        print(data)
        return data

    def retrieve(self, request, *args, **kwargs):
        """Return json or image depending on the format.

        If the accept header is set to an image format `image/*` the image
        file will be returned.

        Use the `size` query paramater to get the corect file size.
        Options are [`thumbnail`, `small`, `medium`, `large`, `original`].
        """
        size = request.query_params.get('size', 'small').lower()
        if size not in image_sizes:
            return Response(data=['Size must be one of [ {} ]'.
                                  format(', '.join(image_sizes))],
                            status=status.HTTP_400_BAD_REQUEST)
        image_object = self.get_object()
        if size == 'original':
            img = image_object
        else:
            try:
                img = ResizedImage.objects.get(image=image_object, size=size)
            except ResizedImage.DoesNotExist:
                img = image_object.resize(size)
        img = img.file

        if request.accepted_renderer.format == 'image':
            # Return the image file.
            return Response(img,
                            content_type='image/{}'.format(image_object.type))
        else:
            data = self.get_serializer(image_object).data
            data['size'] = size
            data['file'] = request.build_absolute_uri(img.url)
            return Response(data)
