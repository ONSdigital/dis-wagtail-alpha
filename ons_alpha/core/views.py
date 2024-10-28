from django.http import HttpResponse


def ready(request):  # pylint: disable=unused-argument
    return HttpResponse("ok", content_type="text/plain")
