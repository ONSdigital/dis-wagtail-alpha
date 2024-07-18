import atexit
import signal

from functools import partial

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, **options):
        self.scheduler = BlockingScheduler(executors={"default": ThreadPoolExecutor()})

        self.setup_signals()

        self.configure_scheduler()

        self.scheduler.start()

    def setup_signals(self):
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        atexit.register(self.shutdown)

    def shutdown(self, *args, **kwargs):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def add_management_command(self, command_name, trigger, **kwargs):
        func = partial(call_command, command_name, **kwargs)
        self.scheduler.add_job(func, name=command_name, trigger=trigger)

    def configure_scheduler(self):
        self.add_management_command("publish_scheduled", CronTrigger(second=0))
