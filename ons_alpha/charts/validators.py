import csv

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


BLANK_VALUES = ("", "NULL", "-", "---")


def csv_file_validator(file):
    # check file valid csv format
    try:
        csv.Sniffer().sniff(file.read(1024))
        file.seek(0)
    except csv.Error as e:
        raise ValidationError(_("The file is not a valid CSV.")) from e
    return True
