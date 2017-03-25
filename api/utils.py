import codecs
import csv


def csv_reader(csv_file, charset):
    """Make sure `csv_file` is a string iterator."""
    return csv.reader(codecs.iterdecode(csv_file, charset))
