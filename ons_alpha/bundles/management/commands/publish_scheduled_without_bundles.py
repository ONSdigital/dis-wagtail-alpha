from django.apps import apps
from django.core.management.base import BaseCommand
from django.utils import dateparse, timezone
from wagtail.models import DraftStateMixin, Page, Revision

from ons_alpha.bundles.models import BundledPageMixin


def revision_date_expired(r):
    expiry_str = r.content.get("expire_at")
    if not expiry_str:
        return False
    expire_at = dateparse.parse_datetime(expiry_str)
    return expire_at < timezone.now()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry-run",
            default=False,
            help="Dry run -- don't change anything.",
        )

    def handle(self, *args, **options):
        dry_run = False
        if options["dry-run"]:
            self.stdout.write("Will do a dry run.")
            dry_run = True

        self._unpublish_expired(dry_run)
        self._publish_scheduled_without_bundles(dry_run)

    def _publish_scheduled_without_bundles(self, dry_run):
        # 2. get all revisions that need to be published
        preliminary_revs_for_publishing = Revision.objects.filter(approved_go_live_at__lt=timezone.now()).order_by(
            "approved_go_live_at"
        )
        revs_for_publishing = []
        for rev in preliminary_revs_for_publishing:
            content_object = rev.as_object()
            if not isinstance(content_object, BundledPageMixin) or not content_object.in_active_bundle:
                revs_for_publishing.append(rev)
        if dry_run:
            self.stdout.write("\n---------------------------------")
            if revs_for_publishing:
                self.stdout.write("Revisions to be published:")
                self.stdout.write("Go live datetime\tModel\t\tSlug\t\tName")
                self.stdout.write("----------------\t-----\t\t----\t\t----")
                for rp in revs_for_publishing:
                    model = rp.content_type.model_class()
                    rev_data = rp.content
                    self.stdout.write(
                        f'{rp.approved_go_live_at.strftime("%Y-%m-%d %H:%M")}\t'
                        f'{model.__name__}\t{rev_data.get("slug", "")}\t\t{rev_data.get("title", rp.object_str)}'
                    )
            else:
                self.stdout.write("No objects to go live.")
        else:
            for rp in revs_for_publishing:
                # just run publish for the revision -- since the approved go
                # live datetime is before now it will make the object live
                rp.publish(log_action="wagtail.publish.scheduled")

    def _unpublish_expired(self, dry_run):
        models = [Page]
        models += [
            model for model in apps.get_models() if issubclass(model, DraftStateMixin) and not issubclass(model, Page)
        ]
        # 1. get all expired objects with live = True
        expired_objects = []
        for model in models:
            expired_objects += [model.objects.filter(live=True, expire_at__lt=timezone.now()).order_by("expire_at")]
        if dry_run:
            self.stdout.write("\n---------------------------------")
            if any(expired_objects):
                self.stdout.write("Expired objects to be deactivated:")
                self.stdout.write("Expiry datetime\t\tModel\t\tSlug\t\tName")
                self.stdout.write("---------------\t\t-----\t\t----\t\t----")
                for queryset in expired_objects:
                    if queryset.model is Page:
                        for obj in queryset:
                            self.stdout.write(
                                f'{obj.expire_at.strftime("%Y-%m-%d %H:%M")}\t'
                                f"{obj.specific_class.__name__}\t{obj.slug}\t{obj.title}"
                            )
                    else:
                        for obj in queryset:
                            self.stdout.write(
                                f'{obj.expire_at.strftime("%Y-%m-%d %H:%M")}\t'
                                f"{queryset.model.__name__}\t\t\t{obj!s}"
                            )
            else:
                self.stdout.write("No expired objects to be deactivated found.")
        else:
            # Unpublish the expired objects
            for queryset in expired_objects:
                # Cast to list to make sure the query is fully evaluated
                # before unpublishing anything
                for obj in list(queryset):
                    obj.unpublish(set_expired=True, log_action="wagtail.unpublish.scheduled")
