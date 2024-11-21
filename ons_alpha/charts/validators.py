import csv

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


BLANK_VALUES = ("", "NULL", "-", "---")


def csv_file_validator(file):
    # check file valid csv format
    with file.open("rb") as csvfile:
        try:
            csv.Sniffer().sniff(csvfile.read(1024).decode("utf-8"))
            file.seek(0)
        except csv.Error as e:
            raise ValidationError(_("The file is not a valid CSV.")) from e
    return True
