from django.contrib import admin
from .models import Batch, Project, SupervisorRequest, SupervisorManage

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch_leader',)
    filter_horizontal = ('members',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'batch', 'domain', 'supervisor')

@admin.register(SupervisorRequest)
class SupervisorRequestAdmin(admin.ModelAdmin):
    list_display = ('batch', 'supervisor', 'status', 'request_date')
    list_filter = ('status',)

@admin.register(SupervisorManage)
class SupervisorManageAdmin(admin.ModelAdmin):
    list_display = ('supervisor', 'max_batches')