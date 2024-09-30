from operator import itemgetter
from typing import TYPE_CHECKING

from django.apps import apps
from django.utils.text import capfirst


if TYPE_CHECKING:
    from ons_alpha.charts.models import Chart


def get_chart_type_models() -> list[type["Chart"]]:
    from ons_alpha.charts.models import Chart  # bypassing circular import

    return [model for model in apps.get_models() if issubclass(model, Chart) and model is not Chart]


def get_chart_type_model_from_name(name) -> type["Chart"]:
    from ons_alpha.charts.models import Chart  # bypassing circular import

    model = apps.get_model(name)
    if not issubclass(model, Chart):
        raise ValueError(f"'{name}' is not a subclass of Chart")
    return model


def get_chart_type_choices() -> list[tuple[str, str]]:
    choices = []
    for model in get_chart_type_models():
        choices.append((model._meta.label_lower, capfirst(model._meta.verbose_name)))
    return sorted(choices, key=itemgetter(1))