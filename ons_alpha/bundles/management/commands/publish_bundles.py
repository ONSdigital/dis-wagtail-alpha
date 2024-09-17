import logging
import time
import uuid

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from wagtail.log_actions import log

from ons_alpha.bundles.enums import BundleStatus
from ons_alpha.bundles.models import Bundle
from ons_alpha.bundles.notifications import notify_slack_of_publication_start, notify_slack_of_publish_end
from ons_alpha.release_calendar.models import ReleaseStatus


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    base_url: str = ""

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Dry run -- don't change anything.",
        )

    def _update_related_release_calendar_page(self, bundle: Bundle):
        content = []
        pages = []
        for page in bundle.get_bundled_pages():
            pages.append(
                {
                    "id": uuid.uuid4(),
                    "type": "item",
                    "value": {"page": page.pk, "title": "", "description": "", "external_url": ""},
                }
            )
        if pages:
            content.append({"type": "release_content", "value": {"title": "Publications", "links": pages}})

        datasets = [{**dataset, "id": uuid.uuid4()} for dataset in bundle.datasets.raw_data]

        page = bundle.release_calendar_page
        page.content = content
        page.datasets = datasets
        page.status = ReleaseStatus.PUBLISHED
        revision = page.save_revision(log_action=True)
        revision.publish()

    @transaction.atomic
    def handle_bundle(self, bundle: Bundle):
        # only provide a URL if we can generate a full one
        inspect_url = self.base_url + reverse("bundle:inspect", args=(bundle.pk,)) if self.base_url else None

        logger.info("Publishing bundle=%d", bundle.id)
        start_time = time.time()
        notify_slack_of_publication_start(bundle, url=inspect_url)
        for page in bundle.get_bundled_pages():
            if (revision := page.scheduled_revision) is None:
                continue
            # just run publish for the revision -- since the approved go
            # live datetime is before now it will make the object live
            revision.publish(log_action="wagtail.publish.scheduled")

        # update the related release calendar and publish
        if bundle.release_calendar_page_id:
            self._update_related_release_calendar_page(bundle)

        bundle.status = BundleStatus.RELEASED
        bundle.save()
        publish_duration = time.time() - start_time
        logger.info("Published bundle=%d duration=%.3fms", bundle.id, publish_duration * 1000)

        notify_slack_of_publish_end(bundle, publish_duration, url=inspect_url)

        log(action="wagtail.publish.scheduled", instance=bundle)

    def handle(self, *args, **options):
        dry_run = False
        if options["dry_run"]:
            self.stdout.write("Will do a dry run.")
            dry_run = True

        self.base_url = getattr(settings, "WAGTAILADMIN_BASE_URL", "")

        bundles_to_publish = Bundle.objects.filter(status=BundleStatus.APPROVED, release_date__lte=timezone.now())
        if dry_run:
            self.stdout.write("\n---------------------------------")
            if bundles_to_publish:
                self.stdout.write("Bundles to be published:")
                for bundle in bundles_to_publish:
                    self.stdout.write(f"- {bundle.name}")
                    bundled_pages = [
                        f"{page.get_admin_display_title()} ({page.__class__.__name__})"
                        for page in bundle.get_bundled_pages().specific()
                    ]
                    self.stdout.write(f'  Pages: {"\n\t ".join(bundled_pages)}')

            else:
                self.stdout.write("No bundles to go live.")
        else:
            for bundle in bundles_to_publish:
                try:
                    self.handle_bundle(bundle)
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.exception("Publish failed bundle=%d", bundle.id)
