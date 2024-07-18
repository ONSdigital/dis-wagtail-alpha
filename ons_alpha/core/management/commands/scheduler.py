import atexit
import logging
import signal

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **options):
        self.scheduler = BlockingScheduler(executors={"default": ThreadPoolExecutor()})

        self.setup_signals()

        self.configure_scheduler()

        logger.info("Starting scheduler")
        self.scheduler.start()

    def setup_signals(self):
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        atexit.register(self.shutdown)

    def shutdown(self, *args, **kwargs):
        if self.scheduler.running:
            logger.info("Shutting down scheduler")
            self.scheduler.shutdown(wait=False)

    def configure_scheduler(self):
        pass
