from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Batch, Project, SupervisorRequest, SupervisorManage
from django.contrib import messages
from apps.site_settings.models import dept_member
from django.db import transaction, IntegrityError
from django.db.models import F
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas


@login_required
def batch_management(request):
    user_email = request.user.email
    try:
        student = dept_member.objects.get(email=user_email)
    except dept_member.DoesNotExist:
        return render(request, "error.html", {"message": "You are not registered as a department member."})

    # Check if user is already in a batch
    batch = Batch.objects.filter(members=student).first()
    if not batch:
        return redirect("create_batch")

    project = getattr(batch, "project", None)
    supervisor_request = SupervisorRequest.objects.filter(batch=batch).first()

    return render(request, "batch_management.html", {
        "batch": batch,
        "project": project,
        "supervisor_request": supervisor_request,
    })


@login_required
def create_batch(request):
    user_email = request.user.email
    leader = get_object_or_404(dept_member, email=user_email)

    # Restrict students who already belong to a batch
    if Batch.objects.filter(members=leader).exists():
        return redirect("batch_management")

    # Students not in any batch (available to be added)
# Students not in any batch (available to be added)
    available_students = dept_member.objects.filter(
        role__icontains="Student",
        catogry__in=["CSP"]
    ).exclude(
        student_batches__isnull=False
    ).exclude(
        id=leader.id  # 👈 Exclude the current user (leader)
    )


    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        domain = request.POST.get("domain", "").strip()
        abstract = request.POST.get("abstract", "").strip()
        selected_students = request.POST.getlist("members")

        # Basic validation
        if not title or not domain or not abstract:
            return render(request, "create_batch.html", {
                "available_students": available_students,
                "error": "All fields are required."
            })

        # Create batch
        batch = Batch.objects.create(batch_leader=leader)
        
        # Add members (leader + selected)
        members_to_add = dept_member.objects.filter(id__in=selected_students)
        batch.members.add(leader, *members_to_add)

        # Create linked project
        Project.objects.create(
            batch=batch,
            title=title,
            domain=domain,
            abstract=abstract
        )

        return redirect("batch_management")

    return render(request, "create_batch.html", {
        "available_students": available_students
    })








@login_required
@transaction.atomic
def request_supervisor(request):
    user_email = request.user.email
    student = get_object_or_404(dept_member, email=user_email)
    batch = Batch.objects.filter(members=student).first()

    if not batch:
        return redirect("create_batch")

    # Lock the batch to prevent concurrent supervisor requests for same batch
    batch = Batch.objects.select_for_update().get(id=batch.id)

    # Get the latest request for this batch
    last_request = SupervisorRequest.objects.filter(batch=batch).order_by("-request_date").first()

    # Prevent new request if last one is still active
    if last_request and last_request.status in ["Pending", "Accepted"]:
        messages.info(request, f"You already have a {last_request.status.lower()} supervisor request.")
        return redirect("batch_management")

    # Fetch supervisors who still have slots
    available_supervisors = dept_member.objects.filter(
        id__in=SupervisorManage.objects.filter(max_batches__gt=0).values_list("supervisor_id", flat=True)
    )

    if request.method == "POST":
        supervisor_id = request.POST.get("supervisor_id")
        supervisor = get_object_or_404(dept_member, id=supervisor_id)

        try:
            # 🔒 Lock the supervisor slot record
            supervisor_slot = SupervisorManage.objects.select_for_update().get(supervisor=supervisor)

            # Check if any slots left
            if supervisor_slot.max_batches <= 0:
                messages.error(request, "This supervisor has reached their supervision limit.")
                return redirect("request_supervisor")

            # If last request was declined, clean it up
            if last_request and last_request.status == "Declined":
                last_request.delete()

            # Create new request safely inside transaction
            SupervisorRequest.objects.create(
                batch=batch,
                supervisor=supervisor,
                status="Pending"
            )

            # Decrease supervisor slot count using F() expression (safe for concurrency)
            supervisor_slot.max_batches = F('max_batches') - 1
            supervisor_slot.save()
            supervisor_slot.refresh_from_db()

            messages.success(request, f"Request sent successfully to {supervisor.name}.")
            return redirect("batch_management")

        except IntegrityError:
            # Handle any race conditions or DB conflicts gracefully
            messages.error(request, "Something went wrong while sending the request. Please try again.", extra_tags="user")
            return redirect("request_supervisor")

    return render(request, "request_supervisor.html", {
        "supervisors": available_supervisors
    })



@login_required
def supervisor_dashboard(request):
    """Display all supervisor requests for the logged-in faculty"""
    user_email = request.user.email

    try:
        supervisor = dept_member.objects.get(email=user_email)
    except dept_member.DoesNotExist:
        return render(request, "error.html", {"message": "You are not registered as a department member."})

    # Check faculty role
    if supervisor.role not in ["Professor", "Associate Professor", "Assistant Professor"]:
        return render(request, "error.html", {"message": "Access Denied: You are not a supervisor."})

    # Get all requests sent to this supervisor
    requests = SupervisorRequest.objects.filter(supervisor=supervisor).select_related('batch__project', 'batch__batch_leader')

    return render(request, "supervisor_requests.html", {"requests": requests})



from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.lib.units import inch
from io import BytesIO
import cloudinary.uploader
import datetime

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch
from io import BytesIO
import datetime
import cloudinary.uploader

@login_required
def update_request_status(request, request_id, action):
    """Allow supervisor to accept or decline a request"""
    user_email = request.user.email
    supervisor = get_object_or_404(dept_member, email=user_email)
    sup_request = get_object_or_404(SupervisorRequest, id=request_id, supervisor=supervisor)
    supervisor_mgmt = get_object_or_404(SupervisorManage, supervisor=supervisor)
    batch = sup_request.batch

    if action == "accept":
        if supervisor_mgmt.max_batches <= 0:
            messages.error(request, "You have reached your supervision limit.", extra_tags="user")
            return redirect("supervisor_dashboard")

        sup_request.status = "Accepted"
        sup_request.save()

        if hasattr(batch, "project"):
            project = batch.project
            project.supervisor = supervisor
            project.save()


        # Define the batch number
        batch_number = getattr(batch, "batch_number", "N/A")  # replace with your batch attribute

        # Function to draw batch number on every page
        def add_batch_number(c, doc):
            """
            c: canvas object
            doc: the document object
            """
            c.saveState()
            # Set font and size
            c.setFont("Times-Roman", 10)
            # Draw batch number at top-right corner
            page_width, page_height = A4
            c.drawRightString(page_width - 60, page_height - 30, f"CSP - Batch No: {batch.id}")
            c.restoreState()

        # When building the PDF, pass the onPage argument


        # === PDF GENERATION ===
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                leftMargin=60, rightMargin=60, topMargin=60, bottomMargin=40)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('title', fontSize=14, alignment=TA_CENTER, spaceAfter=10, fontName='Times-Bold')
        subtitle_style = ParagraphStyle('subtitle', fontSize=11, alignment=TA_CENTER, spaceAfter=6, fontName='Times-BoldItalic')
        normal_style = ParagraphStyle('normal', fontSize=11, leading=15, fontName='Times-Roman')
        justify_style = ParagraphStyle('justify', fontSize=10.5, leading=14, fontName='Times-Roman', alignment=TA_JUSTIFY)

        content = []
        def auto_width_image(path, fixed_height):
            """Return an Image with fixed height and proportional width."""
            img = ImageReader(path)
            iw, ih = img.getSize()
            aspect = iw / float(ih)
            return Image(path, width=fixed_height * aspect, height=fixed_height)

        # === SINGLE CENTERED LOGO ===
        try:
            # Fixed logo height — slightly smaller to fit neatly
            fixed_height = 1 * inch
            logo = auto_width_image("static/images/FULL_VELTECH_LOGO.png", fixed_height)

            # Center the logo exactly in the middle without spacing
            logo_table = Table([[logo]], colWidths=[6.5 * inch])
            logo_table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]))

            # Add the table directly — no extra Spacer
            content.append(logo_table)



        except:
            pass

        content += [
            Spacer(1, 5),   
            Paragraph("SCHOOL OF COMPUTING", subtitle_style),
            Paragraph("<b>DEPARTMENT OF ARTIFICIAL INTELLIGENCE & MACHINE LEARNING (AIML)</b>", subtitle_style),
            Spacer(1, 10),
            Paragraph("<b>PROJECT SUPERVISOR SELECTION FORM</b>", title_style),
            Paragraph("10214AM501 / COMMUNITY SERVICE PROJECT", subtitle_style),
            Paragraph("ACADEMIC YEAR: 2024-2025", subtitle_style),
            Paragraph("SEMESTER: WINTER", subtitle_style),
            Spacer(1, 15),
            Paragraph("I have read and understood the guidelines of the B.Tech. VTR-21 Regulations. "
                      "The details of our Community Service Project area of work are given below:", normal_style),
            Spacer(1, 12),
        ]

        # Paragraph style for wrapping long text
        wrap_style = ParagraphStyle(
            "wrap_style",
            fontName="Times-Roman",
            fontSize=11,
            leading=14,
            textColor=colors.black,
        )

        # Define a wrapping style for paragraphs
        wrap_style = ParagraphStyle(
            name="wrap_style",
            fontName="Times-Roman",
            fontSize=11,
            leading=13,
            alignment=TA_JUSTIFY,
        )

        # Project Info Table
        project_table = [
            [
                Paragraph("<b>PROJECT TITLE:</b>", wrap_style),
                Paragraph(getattr(batch.project, "title", "N/A"), wrap_style),
            ],
            [
                Paragraph("<b>DOMAIN:</b>", wrap_style),
                Paragraph(getattr(batch.project, "domain", "N/A"), wrap_style),
            ],
            [
                Paragraph("<b>TARGETED JOURNAL:</b>", wrap_style),
                Paragraph(getattr(batch.project, "Targeted_Journals", "N/A"), wrap_style),
            ],
        ]

        # Adjusted column widths to prevent line breaks
        t1 = Table(project_table, colWidths=[170, 300])

        t1.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Times-Bold"),  # bold for labels
            ("FONTNAME", (1, 0), (1, -1), "Times-Roman"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
        ]))

        # Center the entire table
        t1.hAlign = "CENTER"

        content.append(t1)
        content.append(Spacer(1, 15))


        # Declaration
        content.append(Paragraph(
            "I hereby declare that I will follow all procedures and guidelines pertaining to the Community Service Project. "
            "I also declare that this project will be carried out under the guidance of the internal supervisor.",
            normal_style,
        ))
        content.append(Spacer(1, 12))

        # Students Table
        data = [["S.No", "VTU No", "Register No", "Name of the Student", "Signature"]]
        for i, member in enumerate(batch.members.all(), start=1):
            data.append([
                str(i),
                getattr(member, "Id_number", ""),
                getattr(member, "reg_no", ""),
                member.name,
                ""
            ])
        student_table = Table(data, colWidths=[40, 80, 90, 200, 80])
        student_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.black),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))
        content.append(student_table)
        content.append(Spacer(1, 15))

        # Supervisor Section
        supervisor_table = [
            ["NAME OF THE SUPERVISOR:", f"{supervisor.name}({supervisor.Id_number})"],
            ["DATE:", str(datetime.date.today())],
        ]
        t2 = Table(supervisor_table, colWidths=[180, 300])
        t2.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        content.append(t2)






        left_style = ParagraphStyle('left', alignment=TA_LEFT, fontName='Times-Roman', fontSize=11)
        right_style = ParagraphStyle('right', alignment=TA_RIGHT, fontName='Times-Roman', fontSize=11)

        # Create bold paragraphs for each signature
        coordinator_sign = Paragraph("<b>(Sign of Project Supervisor)</b>", left_style)
        supervisor_sign = Paragraph("<b>(Sign of Head of the Department)</b>", right_style)

        # Create table with two columns
        sign_table2 = Table(
            [[coordinator_sign, supervisor_sign]],
            colWidths=[250, 250]  # Adjust widths to fit your page (e.g., A4 → 500 total)
        )

        # Apply table styling
        sign_table2.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
            ("LEFTPADDING", (0, 0), (-1, -1), 20),
            ("RIGHTPADDING", (0, 0), (-1, -1), 20),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
        ]))

        # Add spacing before the table and append to content
        content.append(Spacer(1, 70))
        content.append(sign_table2)




        # === PAGE 2 ===
        content.append(PageBreak())


        # === SINGLE CENTERED LOGO ===
        try:
            # Fixed logo height — slightly smaller to fit neatly
            fixed_height = 1 * inch
            logo = auto_width_image("static/images/FULL_VELTECH_LOGO.png", fixed_height)

            # Center the logo exactly in the middle without spacing
            logo_table = Table([[logo]], colWidths=[6.5 * inch])
            logo_table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]))

            # Add the table directly — no extra Spacer
            content.append(logo_table)
        except:
            pass

        content += [
            Spacer(1, 5),   
            Paragraph("SCHOOL OF COMPUTING", subtitle_style),
            Paragraph("DEPARTMENT OF ARTIFICIAL INTELLIGENCE & MACHINE LEARNING", subtitle_style),
            Spacer(1, 8),
            Paragraph("<b>ABSTRACT SUBMISSION FORM</b>", title_style),
            Paragraph("10214AM501 / COMMUNITY SERVICE PROJECT", subtitle_style),
            Paragraph("ACADEMIC YEAR: 2024-2025", subtitle_style),
            Paragraph("SEMESTER: WINTER", subtitle_style),
            Spacer(1, 15),
        ]



        # Project Info Table
        project_table = [
            [
                Paragraph("<b>TITLE:</b>", wrap_style),
                Paragraph(getattr(batch.project, "title", "N/A"), wrap_style),
            ],
            [
                Paragraph("<b>DOMAIN:</b>", wrap_style),
                Paragraph(getattr(batch.project, "domain", "N/A"), wrap_style),
            ],
            [
                Paragraph("<b>SUPERVISOR NAME:</b>", wrap_style),
                Paragraph( f"{supervisor.name}({supervisor.Id_number})", wrap_style),
            ],
        ]

        # Adjusted column widths to prevent line breaks
        t1 = Table(project_table, colWidths=[170, 300])

        t1.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Times-Bold"),  # bold for labels
            ("FONTNAME", (1, 0), (1, -1), "Times-Roman"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
        ]))

        # Center the entire table
        t1.hAlign = "CENTER"

        content.append(t1)
        content.append(Spacer(1, 15))
        # content.append(Spacer(1, 10))

        # Abstract
        content.append(Paragraph("<b>ABSTRACT:</b>", normal_style))
        abstract = getattr(batch.project, "abstract", "No abstract available.")
        content.append(Paragraph(abstract.replace("\n", "<br/>"), justify_style))
        content.append(Spacer(1, 30))
        
        
        # Students Table
        data = [["S.No", "VTU No", "Register No", "Name of the Student", "Signature"]]
        for i, member in enumerate(batch.members.all(), start=1):
            data.append([
                str(i),
                getattr(member, "Id_number", ""),
                getattr(member, "reg_no", ""),
                member.name,
                ""
            ])
        student_table = Table(data, colWidths=[40, 80, 90, 200, 80])
        student_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.black),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))
        content.append(student_table)
        content.append(Spacer(1, 50))
        
        
        left_style = ParagraphStyle('left', alignment=TA_LEFT, fontName='Times-Roman', fontSize=11)
        right_style = ParagraphStyle('right', alignment=TA_RIGHT, fontName='Times-Roman', fontSize=11)

        # Create bold paragraphs for each signature
        coordinator_sign = Paragraph("<b>(Sign of Project Supervisor)</b>", left_style)
        supervisor_sign = Paragraph("<b>(Sign of Deptartment CSP Coordinator)</b>", right_style)

        # Create table with two columns
        sign_table2 = Table(
            [[coordinator_sign, supervisor_sign]],
            colWidths=[250, 250]  # Adjust widths to fit your page (e.g., A4 → 500 total)
        )

        # Apply table styling
        sign_table2.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
            ("LEFTPADDING", (0, 0), (-1, -1), 20),
            ("RIGHTPADDING", (0, 0), (-1, -1), 20),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
        ]))

        # Add spacing before the table and append to content
        content.append(Spacer(1, 70))
        content.append(sign_table2)

        # === Build PDF ===
        doc.build(content, onFirstPage=add_batch_number, onLaterPages=add_batch_number)
        buffer.seek(0)

        # Construct filename dynamically using batch number
        batch_number = getattr(batch, "id", "N/A")
        file_name = f"supervisor_selection_and_abstract_form.pdf"

        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            buffer,
            public_id=file_name,  # sets the "path" + filename in Cloudinary
            resource_type="auto",
            folder=f"VELTECH/CSP/batch_{batch.id}",
            overwrite=True  # optional: overwrite if it exists
        )
        pdf_url = upload_result.get("secure_url")
        batch.pdf_report = pdf_url
        batch.save()

        messages.success(request, f"Accepted request and generated official two-page PDF for {batch}.", extra_tags="user")
        return redirect("supervisor_dashboard")

    elif action == "decline":
        sup_request.status = "Declined"
        sup_request.save()
        supervisor_mgmt.max_batches += 1
        supervisor_mgmt.save()
        messages.info(request, f"You declined the project request from {sup_request.batch}.")
        return redirect("supervisor_dashboard")


@login_required
def accepted_batches(request):
    """Display all batches whose requests were accepted by this supervisor"""
    user_email = request.user.email
    supervisor = get_object_or_404(dept_member, email=user_email)

    # Ensure only faculty roles can access
    if supervisor.role not in ["Professor", "Associate Professor", "Assistant Professor"]:
        return render(request, "error.html", {"message": "Access Denied: You are not a supervisor."})

    # Fetch all accepted requests for this supervisor
    accepted_requests = SupervisorRequest.objects.filter(
        supervisor=supervisor,
        status="Accepted"
    ).select_related("batch__project", "batch__batch_leader")

    return render(request, "supervisor_dashboard.html", {
        "supervisor": supervisor,
        "accepted_requests": accepted_requests,
    })

from django.shortcuts import render, get_object_or_404
from apps.site_settings.models import dept_member
from .models import SupervisorRequest  # adjust path if needed

def view_batch_details(request, batch_id):
    """Show full details of an accepted batch."""
    batch_request = get_object_or_404(SupervisorRequest, batch__id=batch_id, status="Accepted")

    context = {
        "req": batch_request,
    }
    return render(request, "batch_details.html", context)
