from django.conf import settings
from django.shortcuts import render


class ParkingPageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.PARKING_PAGE and not request.path.startswith("/admin/"):
            return render(request, "middleware/parking.html")
        response = self.get_response(request)
        return response
