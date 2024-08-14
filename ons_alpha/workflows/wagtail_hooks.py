from typing import Mapping

from django.http import HttpRequest
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.action_menu import ActionMenuItem, CancelWorkflowMenuItem, WorkflowMenuItem

from ons_alpha.workflows.models import ReadOnlyGroupTask


class ReviewActionMenuItem(ActionMenuItem):
    label = _("Submit review")
    name = "action-readonly-review"

    class Media:
        js = ["workflows/js/action-readonly-review.js"]


@hooks.register("construct_page_action_menu")
def amend_page_action_menu_items(menu_items: list, request: HttpRequest, context: Mapping):
    if not all([context["view"] == "edit", context["locked_for_user"], context.get("page")]):
        return

    page = context["page"]
    task = page.current_workflow_task

    if not isinstance(task, ReadOnlyGroupTask) or request.user.is_superuser:
        return

    if task:
        for idx, menu_item in enumerate(menu_items):
            if isinstance(menu_item, CancelWorkflowMenuItem):
                del menu_items[idx]

        is_final_task = page.current_workflow_state and page.current_workflow_state.is_at_final_task

        workflow_menu_items = []
        for name, label, launch_modal in task.get_actions(page, request.user):
            icon_name = "edit"
            if name == "approve":
                icon_name = "success"

                if is_final_task:
                    label = _("%(label)s and Publish") % {"label": label}

            workflow_menu_items.append(WorkflowMenuItem(name, label, launch_modal, icon_name=icon_name, order=0))

        # insert our custom "review" button to show by default
        # its role is to open up the actions dropdown menu
        menu_items.insert(0, ReviewActionMenuItem())
        menu_items.extend(workflow_menu_items)


@hooks.register("insert_editor_js")
def editor_js():
    # note: remove in a future release of Wagtail
    # needed as PageActionMenu.media doesn't consider the PageActionMenu.default_item media
    return format_html('<script src="{}"></script>', static("workflows/js/action-readonly-review.js"))


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html('<link rel="stylesheet" href="{}">', static("workflows/css/readonly-task.css"))
