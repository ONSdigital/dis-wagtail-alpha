from django.shortcuts import render

from .forms import ExampleForm


def example_form(request):
    if request.method == "POST":
        form = ExampleForm(request.POST)
        form.add_error(None, "An example non-field error.")
        form.add_error("single_line_text", "An example field error.")
    else:
        form = ExampleForm()

    return render(request, "pages/forms/example_form.html", {"form": form})
