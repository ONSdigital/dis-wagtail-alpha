# fmt: off
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from ons_alpha.events.models import EventType
from ons_alpha.news.models import NewsType
from ons_alpha.people.models import PersonType


class EventTypeAdmin(SnippetViewSet):
    model = EventType
    menu_icon = "tag"


class NewsTypeAdmin(SnippetViewSet):
    model = NewsType
    menu_icon = "tag"


class PersonTypeAdmin(SnippetViewSet):
    model = PersonType
    menu_icon = "tag"


class TaxonomiesAdminGroup(SnippetViewSetGroup):
    menu_label = "Taxonomies"
    items = (
        NewsTypeAdmin,
        EventTypeAdmin,
        PersonTypeAdmin,
    )
    menu_icon = "tag"


register_snippet(TaxonomiesAdminGroup)
