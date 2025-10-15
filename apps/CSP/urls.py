from django.urls import path
from . import views

urlpatterns = [
    path('batch-management/', views.batch_management, name='batch_management'),
    path('create-batch/', views.create_batch, name='create_batch'),
    path('request-supervisor/', views.request_supervisor, name='request_supervisor'),
    # path("get-students-same-year/", views.get_students_same_year, name="get_students_same_year"),

    path("supervisor/manage/", views.accepted_batches, name="accepted_batches"),
     path('supervisor/requests/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('update-request/<int:request_id>/<str:action>/', views.update_request_status, name='update_request_status'),
        path("accepted/<int:batch_id>/", views.view_batch_details, name="view_batch_details"),

]
