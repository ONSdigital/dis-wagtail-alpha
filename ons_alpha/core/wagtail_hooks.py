from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.staticfiles import versioned_static


@hooks.register("insert_global_admin_js")
def global_admin_js():
    return format_html("<script src='{}'></script>", versioned_static("js/auto-expand-streamfield.js"))


@hooks.register("register_icons")
def register_icons(icons):
    return icons + [
        "wagtailfontawesomesvg/solid/chart-simple.svg",
        "wagtailfontawesomesvg/solid/table.svg",
        "wagtailfontawesomesvg/solid/table-cells.svg",
    ]
