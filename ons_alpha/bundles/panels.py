from wagtail.admin.panels import HelpPanel


class BundleNotePanel(HelpPanel):
    class BoundPanel(HelpPanel.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.content = self._content_for_instance(self.instance)

        def _content_for_instance(self, instance):
            if not hasattr(instance, "bundles"):
                return ""

            if bundles := instance.bundles:
                content = "This page is in the following bundle(s):<ul>"

                for bundle in bundles:
                    content += f"<li>{bundle.name} (Status: {bundle.get_status_display()})</li>"
                content += "</ul>"
            else:
                content = "This page is not part of any bundles"
            return content
