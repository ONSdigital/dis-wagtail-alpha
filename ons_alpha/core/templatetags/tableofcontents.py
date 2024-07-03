import jinja2

from django_jinja import library


@library.global_function
@library.render_with("templates/components/navigation/table-of-contents.html")
@jinja2.pass_context
def table_of_contents(context, page, attr_name, options=None):  # pylint: disable=unused-argument
    if options is None:
        options = {}

    toc_items = []
    for block in getattr(page, attr_name):
        if hasattr(block.block, "to_table_of_contents_items"):
            toc_items.extend(block.block.to_table_of_contents_items(block.value))

    return {"options": {"lists": [{"itemsList": toc_items}], **options}}
