import wagtail.admin.views.pages.edit

from ons_alpha.workflows.views import EditView as OverriddenView


wagtail.admin.views.pages.edit.EditView.as_view = OverriddenView.as_view
