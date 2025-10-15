from django.db import models
from apps.site_settings.models import dept_member

class Batch(models.Model):
    batch_leader = models.ForeignKey(dept_member, on_delete=models.CASCADE, related_name='leader_batches', null=True, blank=True)
    members = models.ManyToManyField(dept_member, related_name='student_batches')

    def __str__(self):
        return f"Batch {self.id} - Leader: {self.batch_leader}"


class Project(models.Model):
    batch = models.OneToOneField(Batch, on_delete=models.CASCADE, related_name='project')
    title = models.CharField(max_length=200)
    domain = models.CharField(max_length=100)
    abstract = models.TextField()
    supervisor = models.ForeignKey(
        dept_member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role__in': ['Professor', 'Associate Professor', 'Assistant Professor']}
    )

    def __str__(self):
        return self.title


class SupervisorRequest(models.Model):
    batch = models.OneToOneField(Batch, on_delete=models.CASCADE,unique=False)
    supervisor = models.ForeignKey(dept_member, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Declined', 'Declined')], default='Pending')
    request_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Request by {self.batch} to {self.supervisor.name} ({self.status})"




class SupervisorManage(models.Model):
    supervisor = models.ForeignKey(
        dept_member,
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['Professor', 'Associate Professor', 'Assistant Professor']}
    )
    max_batches = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.supervisor.name} - Remaining Slots: {self.max_batches}"

    class Meta:
        verbose_name = "Supervisor Management"
        verbose_name_plural = "Supervisor Management"
