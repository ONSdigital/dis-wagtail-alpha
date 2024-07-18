import logging

from django.conf import settings
from django.utils.html import format_html
from slack_sdk.webhook import WebhookClient
from wagtail import hooks
from wagtail.admin.staticfiles import versioned_static


logger = logging.getLogger("ons_alpha.core")


@hooks.register("insert_global_admin_js")
def global_admin_js():
    return format_html("<script src='{}'></script>", versioned_static("js/auto-expand-streamfield.js"))


@hooks.register("register_icons")
def register_icons(icons):
    return icons + [
        "wagtailfontawesomesvg/solid/chart-simple.svg",
    ]


@hooks.register("after_publish_page", order=float("inf"))
def notify_slack_of_publish(request, page):
    if (webhook_url := settings.SLACK_PUBLISH_NOTIFICATION_WEBHOOK_URL) is None:
        return

    revision = page.latest_revision
    user = revision.user

    client = WebhookClient(webhook_url)

    response = client.send(
        text="A new page has been published",
        attachments=[
            {
                "color": "good",
                "fields": [
                    {"title": "Title", "value": page.title, "short": True},
                    {"title": "Published by", "value": user.get_full_name() if user else "System", "short": True},
                    {"title": "Link", "value": page.get_full_url(request=request), "short": False},
                ],
            }
        ],
        unfurl_links=False,
        unfurl_media=False,
    )

    if response.status_code != 200:
        logger.error("Unable to notify slack of page publish: %s", response.body)
