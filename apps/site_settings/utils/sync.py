# from .google_sheets import get_sheet
# from internship.models import InternshipApplication

# def sync_to_sheet():
#     sheet = get_sheet()
#     sheet.clear()
#     sheet.append_row([
#         "ID", "Student Name", "VTU Number", "Department", "Industry", 
#         "Location", "Domain", "Approval Status", "Submitted At"
#     ])

#     for app in InternshipApplication.objects.all():
#         sheet.append_row([
#             app.id,
#             app.student_name,
#             app.vtu_number,
#             app.department,
#             app.industry_name,
#             app.industry_location,
#             app.domain_of_work,
#             app.application_approved,
#             str(app.submitted_at)
#         ])


# def sync_from_sheet():
#     sheet = get_sheet()
#     rows = sheet.get_all_records()

#     for row in rows:
#         InternshipApplication.objects.update_or_create(
#             id=row["ID"],
#             defaults={
#                 "student_name": row["Student Name"],
#                 "vtu_number": row["VTU Number"],
#                 "department": row["Department"],
#                 "industry_name": row["Industry"],
#                 "industry_location": row["Location"],
#                 "domain_of_work": row["Domain"],
#                 "application_approved": row["Approval Status"],
#             }
#         )
