from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from wagtail.images import get_image_model
from wagtail.images.exceptions import InvalidFilterSpecError
from wagtail.images.models import SourceImageIOError
from wagtail.images.utils import verify_signature


Image = get_image_model()


class ONSImageServeView(RedirectView):
    """
    A modified version of Wagtail's `ImageServeView` which validates collection permissions before serving.
    """

    def get_redirect_url(self, signature, image_id, filter_spec, *args, **kwargs):  # pylint: disable=arguments-differ
        if not verify_signature(signature.encode(), image_id, filter_spec):
            raise PermissionDenied

        image = get_object_or_404(Image.objects.select_related("collection"), id=image_id)

        if not all(
            restriction.accept_request(self.request) for restriction in image.collection.get_view_restrictions()
        ):
            raise PermissionDenied

        try:
            rendition = image.get_rendition(filter_spec)
        except SourceImageIOError:
            return HttpResponse("Source image file not found", content_type="text/plain", status=410)
        except InvalidFilterSpecError:
            return HttpResponse(
                f"Invalid filter spec: {filter_spec}",
                content_type="text/plain",
                status=400,
            )

        # NB: .url is overridden
        return rendition.media_url
