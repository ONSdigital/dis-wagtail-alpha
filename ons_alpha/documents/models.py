from wagtail.documents.models import AbstractDocument
from wagtail.documents.models import Document as WagtailDocument

from ons_alpha.private_media.models import PrivateDocumentMixin


class CustomDocument(PrivateDocumentMixin, AbstractDocument):
    admin_form_fields = WagtailDocument.admin_form_fields
