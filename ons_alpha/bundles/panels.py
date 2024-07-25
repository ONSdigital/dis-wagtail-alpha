from django.utils.html import format_html, format_html_join
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
                content_html = format_html_join(
                    "\n",
                    "<li>{} (Status: {})</li>",
                    (
                        (
                            bundle.name,
                            bundle.get_status_display(),
                        )
                        for bundle in bundles
                    ),
                )

                content = format_html("<p>This page is in the following bundle(s):</p><ul>{}</ul>", content_html)
            else:
                content = format_html("<p>This page is not part of any bundles</p>")
            return content
