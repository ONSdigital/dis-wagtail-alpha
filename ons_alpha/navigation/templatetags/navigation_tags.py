from django import template


register = template.Library()


# Primary nav snippets
@register.inclusion_tag("components/navigation/primary_nav.html", takes_context=True)
def primary_nav(context):
    request = context["request"]
    return {
        "primary_nav": context["settings"]["navigation"][
            "NavigationSettings"
        ].primary_navigation,
        "request": request,
    }


# Secondary nav snippets
@register.inclusion_tag("components/navigation/secondary_nav.html", takes_context=True)
def secondary_nav(context):
    request = context["request"]
    return {
        "secondary_nav": context["settings"]["navigation"][
            "NavigationSettings"
        ].secondary_navigation,
        "request": request,
    }


# Footer nav snippets
@register.inclusion_tag("components/navigation/footer_nav.html", takes_context=True)
def footer_nav(context):
    request = context["request"]
    return {
        "footer_nav": context["settings"]["navigation"][
            "NavigationSettings"
        ].footer_navigation,
        "request": request,
    }
