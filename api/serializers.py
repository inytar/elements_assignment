from rest_framework import serializers

from api.image_downloader import ImageDownloader
from api.models import CSV, Image
from api.utils import csv_reader


class CSVSerializer(serializers.HyperlinkedModelSerializer):

    def validate_csv_file(self, upload_file):
        """Validate that the file is parsable by the python csv module."""
        # Basic user protection, test that file ends with '.csv'
        if not upload_file.name.endswith('.csv'):
            raise serializers.ValidationError('File does not end with ".csv".')

        # Test that the file is readable by the python csv module.
        # Get file charset if set by client.
        charset = upload_file.charset or 'utf-8'
        try:
            reader = csv_reader(upload_file, charset)
            # Save the csv header for later.
            self._csv_headers = next(reader)
        except Exception:
            raise serializers.ValidationError('Could not read csv file.')
        return upload_file

    def create(self, validated_data):
        """Set name, charset and header before creation, download images."""
        csv_file = validated_data['csv_file']
        validated_data['name'] = csv_file.name
        charset = csv_file.charset or 'utf-8'
        validated_data['charset'] = charset
        header = validated_data['header'] or []

        # Get headers from file if it has a header, else create generic
        # header.
        if validated_data['has_header']:
            csv_header = self._csv_headers
        else:
            csv_header = ['column %s' % i for i, _ in
                          enumerate(self._csv_headers, 1)]

        # Set the header in validated data. Only sets header values not
        # set by the user.
        validated_data['header'] = header + csv_header[len(header):]
        # In a different process download images.
        ImageDownloader(csv_file, charset).start()
        return super().create(validated_data)

    class Meta:
        model = CSV
        fields = ('url', 'id', 'name', 'uploaded', 'has_header', 'header',
                  'csv_file')
        extra_kwargs = {
            'header': {'required': False},
            'name': {'read_only': True},
        }


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Image
        fields = ('url', 'id', 'uploaded', 'type',
                  'original_url', 'original_file')
