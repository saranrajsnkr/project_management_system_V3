import datetime
from django.conf import settings
from django.shortcuts import render
from apps.site_settings.models import SiteSetting
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import AnonymousUser



# settings.py
COMPANY_OPEN_PATHS = ("/company/login", "/company/attendance")

class ForceLogoutOnCompanyPathsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.rstrip("/")
        # match "/company/login" and anything under it like "/company/login/..."
        def matches(p): 
            return path == p or path.startswith(p + "/")

        if any(matches(p) for p in getattr(settings, "COMPANY_OPEN_PATHS", ())):
            if request.user.is_authenticated:
                logout(request)                 # flush session + rotate key
                request.user = AnonymousUser()  # make this request anonymous immediately
            return self.get_response(request)

        return self.get_response(request)

from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from apps.site_settings.models import dept_member  # <-- import your model (change app name if needed)



class DomainRestrictMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user = request.user
            email = user.email or ""

            # 🛑 Skip restriction for superusers or staff (admin panel users)
            if user.is_superuser or user.is_staff:
                return self.get_response(request)

            # ✅ Step 1: Check email domain
            if not email.endswith("@veltech.edu.in"):
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Only @veltech.edu.in emails are allowed.",
                    # extra_tags='domain_error'
                )
                logout(request)
                return redirect("custom_login")

            # #✅ Step 2: Check if email exists in DeptMember
            # if not dept_member.objects.filter(email__iexact=email).exists():
            #     messages.add_message(
            #         request,
            #         messages.ERROR,
            #         "Email is not in the AIML department.",
            #         # extra_tags='domain_error'
            #     )
            #     logout(request)
            #     return redirect("custom_login")

        return self.get_response(request)


# internship_portal/middleware.py
from django.conf import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.rstrip("/")
        def matches(p): 
            return path == p or path.startswith(p + "/")

        # Always allowed, no login required
        if any(matches(p) for p in settings.COMPANY_OPEN_PATHS):
            return self.get_response(request)

        exempt_paths = ("/accounts", "/login", "/static", "/favicon.ico")
        if (
            not request.user.is_authenticated
            and not any(path.startswith(p) for p in exempt_paths)
        ):
            from django.shortcuts import redirect
            return redirect("custom_login")
        return self.get_response(request)



class AdminLoginBypassMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            # Disable social login for admin
            request.session['skip_social_login'] = True
        return self.get_response(request)



class RoleBasedSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        now = datetime.datetime.now().timestamp()

        if request.user.is_staff or request.user.is_superuser:
            # Admin → idle timeout
            idle_timeout = getattr(settings, "ADMIN_IDLE_TIMEOUT", 1800)  # default 15 mins
            last_activity = request.session.get("last_activity", now)

            if now - last_activity > idle_timeout:
                logout(request)
                request.session.flush()
            else:
                request.session["last_activity"] = now

        else:
            # Normal users → absolute timeout (default Django behavior)
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)

        return self.get_response(request)
