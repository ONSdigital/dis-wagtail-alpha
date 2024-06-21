import factory
import wagtail_factories
from faker import Factory as FakerFactory

from .models import EventIndexPage, EventPage

faker = FakerFactory.create()


class EventPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = EventPage

    title = factory.Faker("text", max_nb_chars=25)
    introduction = factory.Faker("text", max_nb_chars=100)
    start_date = factory.Faker("date_object")


class EventIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = EventIndexPage
