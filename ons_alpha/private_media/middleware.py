from django.shortcuts import redirect
from wagtail.admin import messages


class PreventRootCollectionChangesMiddleware:
    """
    A custom Middleware that prevents editing or deletion of the special 'Private' and
    'Public' collections used by this project to restrict access to private media.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):  # pylint: disable=unused-argument
        from ons_alpha.private_media import utils  # pylint: disable=import-outside-toplevel

        if getattr(request.resolver_match, "view_name", "") == "wagtailadmin_collections:edit" and int(
            view_kwargs["pk"]
        ) in (utils.get_private_root_collection_id(), utils.get_public_root_collection_id()):
            messages.warning(
                request,
                "Sorry, the root collections for this project are protected and cannot be edited.",
            )
            return redirect("wagtailadmin_collections:index")
        if getattr(request.resolver_match, "view_name", "") == "wagtailadmin_collections:delete" and int(
            view_kwargs["pk"]
        ) in (utils.get_private_root_collection_id(), utils.get_public_root_collection_id()):
            messages.warning(
                request,
                "Sorry, the root collections for this project are protected and cannot be deleted.",
            )
            return redirect("wagtailadmin_collections:index")
        return None
