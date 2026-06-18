from django.contrib import admin, messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import F
import csv

from .models import dept_member
from .forms import CsvImportForm  # Make sure you have this form defined
from .models import dept_member, SiteSetting, Announcement, downloadable_files


@admin.register(dept_member)
class DeptMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "Id_number", "email", "phone", "role", "catogry")
    search_fields = ("name", "Id_number", "email")
    list_filter = ("role","catogry")
    ordering = ("name",)
    actions = ["export_as_csv"]
    change_list_template = "admin/changelist.html"  # custom changelist with upload button

    # ✅ EXPORT CSV
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="dept_members.csv"'
        writer = csv.writer(response)

        # CSV Header
        writer.writerow(["Name", "VTU/TTS Number","Registration Number", "Email", "Phone", "Role", "Catogry"])

        # CSV Rows
        for member in queryset:
            writer.writerow([
                member.name,
                member.Id_number,
                member.reg_no,
                member.email,
                member.phone or '',
                member.role or '',
                member.catogry or '',
            ])

        return response

    export_as_csv.short_description = "Export Selected Department Members to CSV"

    # ✅ CUSTOM ADMIN URL FOR IMPORT
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path("upload-csv/", self.upload_csv),
        ]
        return custom_urls + urls

    # ✅ IMPORT CSV HANDLER
    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES.get("csv_upload")
            if not csv_file or not csv_file.name.endswith(".csv"):
                messages.error(request, "Please upload a valid CSV file.")
                return redirect("..")

            try:
                try:
                    decoded_file = csv_file.read().decode("utf-8").splitlines()
                except UnicodeDecodeError:
                    csv_file.seek(0)
                    decoded_file = csv_file.read().decode("latin-1").splitlines()

                reader = csv.DictReader(decoded_file)

                for row in reader:
                    try:
                        id_number = row.get("VTU/TTS Number", "").strip()
                        if not id_number:
                            self.message_user(request, "Skipping row with empty ID number.", level=messages.WARNING)
                            continue

                        # Prevent duplicate ID entries
                        if dept_member.objects.filter(Id_number=id_number).exists():
                            self.message_user(request, f"Duplicate ID {id_number} skipped.", level=messages.WARNING)
                            continue

                        dept_member.objects.create(
                            name=row.get("Name", "").strip(),
                            Id_number=id_number,
                            reg_no=row.get("Registration Number", "").strip(),
                            email=row.get("Email", "").strip(),
                            phone=row.get("Phone", "").strip(),
                            role=row.get("Role", "").strip(),
                            catogry=row.get("Catogry", "").strip() if "Catogry" in row else None,
                        )

                    except Exception as e:
                        self.message_user(request, f"Error importing row: {row} → {e}", level=messages.ERROR)

                messages.success(request, "CSV file imported successfully.")
                return redirect("..")

            except Exception as e:
                messages.error(request, f"Error processing file: {e}")
                return redirect("..")

        # GET request – show upload form
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "admin/csv_upload.html", payload)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("SiteSettings", "maintenance_mode", "max_students_per_batch")
    list_editable = ("maintenance_mode", "max_students_per_batch")
    ordering = ("SiteSettings",)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "id", "is_message1_active", "message1_color",
        "is_message2_active", "message2_color"
    )
    list_display_links = ("id",)  # <-- make 'id' clickable
    list_editable = (
        "is_message1_active", "message1_color",
        "is_message2_active", "message2_color"
    )
    ordering = ("id",)



@admin.register(downloadable_files)
class DownloadableFilesAdmin(admin.ModelAdmin):
    list_display = ("file_name", "file_link")
    search_fields = ("file_name",)
    ordering = ("file_name",)
