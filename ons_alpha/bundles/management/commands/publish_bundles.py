from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from ons_alpha.bundles.models import Bundle, BundleStatus


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Dry run -- don't change anything.",
        )

    @transaction.atomic
    def handle_bundle(self, bundle: Bundle):
        bundled_pages = bundle.get_bundled_pages()

        bundled_revisions = [page.scheduled_revision for page in bundled_pages if page.scheduled_revision]
        for revision in bundled_revisions:
            # just run publish for the revision -- since the approved go
            # live datetime is before now it will make the object live
            revision.publish(log_action="wagtail.publish.scheduled")

        # update the related release calendar and publish

        bundle.status = BundleStatus.RELEASED
        bundle.save()

    def handle(self, *args, **options):
        dry_run = False
        if options["dry_run"]:
            self.stdout.write("Will do a dry run.")
            dry_run = True

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
                self.handle_bundle(bundle)
