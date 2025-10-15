from django.shortcuts import render, redirect, get_object_or_404
from .models import  Announcement , downloadable_files , SiteSetting, dept_member
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import F
from django.http import JsonResponse
import psutil
import os
from django.core.mail import send_mail
import random
from django.conf import settings
import gspread
from google.oauth2.service_account import Credentials
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
import re
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
import cloudinary.uploader
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
import datetime
from django.db.models import Q
import json
from django.http import JsonResponse, HttpResponseBadRequest

# Setup Google credentials
# SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# creds = Credentials.from_service_account_info(settings.GOOGLE_CONFIG, scopes=SCOPES)
# client = gspread.authorize(creds)
# sheet = client.open_by_key(settings.GOOGLE_SHEET_ID).sheet1


def home(request):
    if request.user.is_authenticated:
        username = request.user.username
        name = request.user.first_name
        email = request.user.email
        rollno = email.split("@")[0]

        if rollno.startswith("vtu") and rollno[3:].isdigit():
            Vtu_number = rollno[3:]   # only the numbers
        else:
            Vtu_number = None

        announcement = Announcement.objects.first()

        # check admin
        is_admin = request.user.is_superuser or request.user.is_staff

        try:
            dept_user = dept_member.objects.get(email=email)
            user_role = dept_user.role
        except dept_member.DoesNotExist:
            user_role = "Unknown"
            
        return render(
            request,
            "home.html",
            {
                "rollno": rollno,
                "announcement": announcement,
                "name": name,
                "email": email,
                "username": username,
                "Vtu_number": Vtu_number,
                "path": request.path,
                "is_admin": is_admin,   # pass to template
                "user_role": user_role,
            },
        )

# def sitelogin(request):
#     return render(request, 'internship/site_login.html')

@login_required
def account_dashboard(request):
    if request.user.is_authenticated:
        username = request.user.username
        name = request.user.first_name
        email = request.user.email
        rollno = email.split("@")[0]

        if rollno.startswith("vtu") and rollno[3:].isdigit():
            Vtu_number = rollno[3:]   # only the numbers
        else:
            Vtu_number = None


        # check admin
        is_admin = request.user.is_superuser or request.user.is_staff
        
        # Check Student model
        

        site_settings = SiteSetting.objects.first()

        return render(
            request,
            "dashboard.html",
            {
                "rollno": rollno,
                "name": name,
                "email": email,
                "username": username,
                "Vtu_number": Vtu_number,
                "path": request.path,
                "is_admin": is_admin,   # pass to template
                "site_setting": site_settings,
            },
        )




def performance_view(request):
    pid = os.getpid()
    process = psutil.Process(pid)

    cpu = process.cpu_percent(interval=0.5)
    memory = process.memory_info().rss / 1024 ** 2  # in MB

    return JsonResponse({
        "cpu_usage_percent": f"{cpu:.2f}",
        "memory_usage_mb": f"{memory:.2f}"
    })




def csrf_failure(request, reason=""):
    path = request.path
    
    # Default/common CSRF failure page
    return render(request, "internship/common_csrf_failure.html", status=403)


def handler404(request, exception):
    return render(request, "errors/404.html", status=404)

def handler500(request):
    return render(request, "errors/500.html", status=500)

def handler403(request, exception=None):
    return render(request, "errors/403.html", status=403)

def handler400(request, exception):
    return render(request, "errors/400.html", status=400)


def downloadable_files_view(request):
    files = downloadable_files.objects.all()
    return render(request, 'downloadable_files.html', {'files': files})