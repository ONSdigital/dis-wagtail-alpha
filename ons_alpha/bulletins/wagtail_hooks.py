from django.utils.timezone import now
from wagtail import hooks

from ons_alpha.bulletins.models import BulletinPage


@hooks.register("before_publish_page")
def handle_link_to_release_calendar(request, page):  # pylint: disable=unused-argument
    if not isinstance(page, BulletinPage):
        return

    if page.release_calendar_page and page.release_calendar_page.release_date > now():
        page.go_live_at = page.release_calendar_page.release_date
