from django.db.models import Model
from django.http.request import QueryDict
from django import template

register = template.Library()

MODE_ADD = "__add"
MODE_REMOVE = "__remove"
MODE_TOGGLE = "__toggle"


@register.simple_tag(takes_context=True)
def querystring_modify(
    context, base=None, remove_blanks=False, remove_utm=True, **kwargs
):
    """
    Renders a URL and IRI encoded querystring that is safe to include in links.
    """
    querydict = get_base_querydict(context, base)

    for key, value in kwargs.items():
        if isinstance(value, Model):
            value = str(value.pk)
        elif value is not None and not hasattr(value, "__iter__"):
            value = str(value)

        if key.endswith(MODE_TOGGLE):
            handle_toggle(querydict, key, value)

        elif key.endswith(MODE_ADD):
            handle_add(querydict, key, value)

        elif key.endswith(MODE_REMOVE):
            handle_remove(querydict, key, value)

        elif value is None:
            querydict.pop(key, None)

        else:
            handle_default(querydict, key, value)

    clean_querydict(querydict, remove_blanks, remove_utm)

    return f"?{querydict.urlencode()}"

def get_base_querydict(context, base):
    """
    Retrieves the base QueryDict object based on provided context or base value.
    """
    if base is None and "request" in context:
        return context["request"].GET.copy()
    if isinstance(base, QueryDict):
        return base.copy()
    if isinstance(base, dict):
        return QueryDict.fromkeys(base, mutable=True)
    if isinstance(base, str):
        return QueryDict(base, mutable=True)
    # Request not present or base value unsupported
    return QueryDict("", mutable=True)


def clean_querydict(querydict, remove_blanks=False, remove_utm=True):
    """
    Cleans the QueryDict by removing blank values and optionally removing
    'utm_*' parameters.
    """
    remove_vals = {None}
    if remove_blanks:
        remove_vals.add("")

    if remove_utm:
        for key in list(querydict.keys()):
            if key.lower().startswith("utm_"):
                querydict.pop(key)

    for key, values in list(querydict.lists()):
        cleaned_values = [v for v in values if v not in remove_vals]
        if cleaned_values:
            querydict.setlist(key, cleaned_values)
        else:
            del querydict[key]

def handle_toggle(querydict, key, value):
    key = key[:-len(MODE_TOGGLE)]
    values = set(querydict.getlist(key))
    if value in values:
        values.remove(value)
    else:
        values.add(value)
    querydict.setlist(key, list(values))

def handle_add(querydict, key, value):
    key = key[:-len(MODE_ADD)]
    values = set(querydict.getlist(key))
    if value not in values:
        values.add(value)
        querydict.setlist(key, list(values))

def handle_remove(querydict, key, value):
    key = key[:-len(MODE_REMOVE)]
    values = set(querydict.getlist(key))
    if value in values:
        values.remove(value)
        querydict.setlist(key, list(values))

def handle_default(querydict, key, value):
    if isinstance(value, str | bytes):
        querydict[key] = value
    elif hasattr(value, "__iter__"):
        querydict.setlist(key, list(value))
