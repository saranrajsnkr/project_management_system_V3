from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Batch, Project, SupervisorRequest, SupervisorManage
from django.contrib import messages
from apps.site_settings.models import dept_member
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

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
@transaction.atomic  # ✅ Ensures all DB operations happen as a single atomic transaction
def request_supervisor(request):
    user_email = request.user.email
    student = get_object_or_404(dept_member, email=user_email)
    batch = Batch.objects.filter(members=student).first()

    if not batch:
        return redirect("create_batch")

    # Get the latest request for this batch
    last_request = SupervisorRequest.objects.filter(batch=batch).order_by("-request_date").first()

    # If there is a pending or accepted request → block new requests
    if last_request and last_request.status in ["Pending", "Accepted"]:
        messages.info(request, f"You already have a {last_request.status.lower()} supervisor request.")
        return redirect("batch_management")

    # Fetch only supervisors who still have available slots
    supervisor_slots = SupervisorManage.objects.select_for_update().filter(max_batches__gt=0)
    available_supervisors = dept_member.objects.filter(
        id__in=supervisor_slots.values_list("supervisor_id", flat=True)
    )

    if request.method == "POST":
        supervisor_id = request.POST.get("supervisor_id")
        supervisor = get_object_or_404(dept_member, id=supervisor_id)

        # Lock this supervisor row to prevent race condition
        supervisor_slot = SupervisorManage.objects.select_for_update().get(supervisor=supervisor)

        # Check slot availability before creating request
        if supervisor_slot.max_batches <= 0:
            messages.error(request, "This supervisor has reached their supervision limit.")
            return redirect("request_supervisor")

        # 🔹 If last request was declined, delete it before creating new one
        if last_request and last_request.status == "Declined":
            last_request.delete()

        # Create new request and reduce supervisor slot
        SupervisorRequest.objects.create(batch=batch, supervisor=supervisor, status="Pending")
        supervisor_slot.max_batches -= 1
        supervisor_slot.save()

        messages.success(request, f"Request sent successfully to {supervisor.name}.")
        return redirect("batch_management")

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




@login_required
def update_request_status(request, request_id, action):
    """Allow supervisor to accept or decline a request"""
    user_email = request.user.email
    supervisor = get_object_or_404(dept_member, email=user_email)
    sup_request = get_object_or_404(SupervisorRequest, id=request_id, supervisor=supervisor)

    # Get supervisor management record
    supervisor_mgmt = get_object_or_404(SupervisorManage, supervisor=supervisor)

    if action == "accept":
        # Check supervisor batch quota
        if supervisor_mgmt.max_batches <= 0:
            messages.error(request, "You have reached your supervision limit.")
            return redirect("supervisor_dashboard")

        sup_request.status = "Accepted"
        sup_request.save()

        # Assign supervisor to project (if project relation exists)
        if hasattr(sup_request.batch, "project"):
            project = sup_request.batch.project
            project.supervisor = supervisor
            project.save()

        # # Decrease available batch count
        # supervisor_mgmt.max_batches -= 1
        # supervisor_mgmt.save()

        messages.success(request, f"You have accepted the project request from {sup_request.batch}.")

    elif action == "decline":
        sup_request.status = "Declined"
        sup_request.save()

        # Increase available batch count back
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
