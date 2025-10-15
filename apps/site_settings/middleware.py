from django.shortcuts import render
from .models import SiteSetting
from django.shortcuts import redirect

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            setting = SiteSetting.objects.first()
            maintenance = setting.maintenance_mode if setting else False
        except:
            maintenance = False
        


        # Block non-staff users if maintenance is ON
        if maintenance and not request.user.is_staff:
            return render(request, "maintenance.html", status=503)

        return self.get_response(request)
