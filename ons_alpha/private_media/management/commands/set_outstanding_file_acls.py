from django.core.management.base import BaseCommand
from django.db.models import F

from ons_alpha.private_media.constants import PRIVATE_FILE_ACL, PUBLIC_FILE_ACL
from ons_alpha.private_media.signal_handlers import get_private_media_models


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Dry run -- don't change anything.",
        )

    def handle(self, *args, **options):
        dry_run = False
        if options["dry_run"]:
            self.stdout.write("This is a dry run.")
            dry_run = True

        for model in get_private_media_models():
            acls_needs_updating = list(model.objects.filter(acls_last_set__lt=F("privacy_last_changed")))
            self.stdout.write(f"{len(acls_needs_updating)} {model.__name__} instances require ACL updates")
            if acls_needs_updating and not dry_run:

                private = []
                public = []
                for obj in acls_needs_updating:
                    if obj.is_private:
                        private.append(obj)
                    else:
                        public.append(obj)

                if private:
                    private_result = model.objects.bulk_set_file_acls(private, PRIVATE_FILE_ACL)
                    self.stdout.write(
                        f"ACLs successfully set for {private_result} private {model._meta.verbose_name_plural}"
                    )
                if public:
                    public_result = model.objects.bulk_set_file_acls(private, PUBLIC_FILE_ACL)
                    self.stdout.write(
                        f"ACLs successfully set for {public_result} public items {model._meta.verbose_name_plural}"
                    )
