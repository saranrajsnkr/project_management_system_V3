# import gspread
# from google.oauth2.service_account import Credentials
# from django.conf import settings
# from internship.models import Student, Company
# import time


# # Setup Google credentials
# SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# creds = Credentials.from_service_account_info(settings.GOOGLE_CONFIG, scopes=SCOPES)
# client = gspread.authorize(creds)
# sheet = client.open_by_key(settings.GOOGLE_SHEET_ID).sheet1


# def sync_db_to_sheets():
#     """Push all Student rows → Google Sheets"""
#     students = Student.objects.all()

#     # Clear existing sheet data
#     sheet.clear()

#     # Add header row
#     sheet.append_row(["ID", "Name", "Roll Number", "Mobile Number", "Department", "Company", "Fee"])

#     for s in students:
#         sheet.append_row([
#             s.id,
#             s.name,
#             s.roll_number,
#             s.mobile_number or "",
#             s.department or "",
#             s.applied_company.name if s.applied_company else "",
#             s.fee or ""
#         ])
#         time.sleep(2)