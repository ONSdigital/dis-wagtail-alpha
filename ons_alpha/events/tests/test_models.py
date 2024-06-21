from wagtail.test.utils import WagtailPageTestCase

from ons_alpha.events.factories import (
    EventIndexPageFactory,
    EventPageFactory,
)
from ons_alpha.events.models import EventIndexPage, EventPage
from ons_alpha.home.models import HomePage


class EventsTests(WagtailPageTestCase):
    def test_factories(self):
        EventPageFactory()
        EventIndexPageFactory()

    def test_can_create_event_index_page_under_home_page(self):
        self.assertCanCreateAt(HomePage, EventIndexPage)

    def test_can_create_event_page_under_event_index_page(self):
        self.assertCanCreateAt(EventIndexPage, EventPage)
