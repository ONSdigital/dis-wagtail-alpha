from wagtail.test.utils import WagtailPageTestCase

from ons_alpha.home.models import HomePage
from ons_alpha.people.factories import (
    PersonIndexPageFactory,
    PersonPageFactory,
)
from ons_alpha.people.models import PersonIndexPage, PersonPage


class PeopleTests(WagtailPageTestCase):
    def test_factories(self):
        PersonPageFactory()
        PersonIndexPageFactory()

    def test_can_create_person_page_under_home_page(self):
        self.assertCanCreateAt(HomePage, PersonIndexPage)

    def test_can_create_person_page_under_person_index_page(self):
        self.assertCanCreateAt(PersonIndexPage, PersonPage)
