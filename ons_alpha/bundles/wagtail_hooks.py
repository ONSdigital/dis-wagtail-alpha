from wagtail import hooks

from .viewsets import bundle_chooser_viewset, bundle_viewset


@hooks.register("register_admin_viewset")
def register_viewset():
    return [bundle_viewset, bundle_chooser_viewset]
