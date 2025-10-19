from django.db import models

# Create your models here.
# models.py

        
class dept_member(models.Model):
    Role_choices = [('2nd Year Student', '2nd Year Student'),
                    ('3rd Year Student', '3rd Year Student'),
                    ('4th Year Student', '4th Year Student'),
                    ('HOD', 'HOD'),
                    ('Associate Professor', 'Associate Professor'),
                    ('Assistant Professor', 'Assistant Professor'),
                    ('Professor', 'Professor'),
                    ('Lab Assistant', 'Lab Assistant'),
                    ('Admin Staff', 'Admin Staff'),
                    ('Other', 'Other')]
    Catogry_choices = [('CSP', 'CSP'),
                       ('Minor 1', 'Minor 1'),
                       ('Minor 2', 'Minor 2'),
                       ('Major', 'Major'),
                       ('Staff', 'Staff'),]
    
    name = models.CharField(max_length=100)
    Id_number = models.CharField("VTU/TTS Number", max_length=20, unique=True, help_text="Enter VTU/TTS Number", blank=True, null=True)
    reg_no = models.CharField("Registration Number", max_length=20, unique=True, help_text="Enter Registration Number", blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=50, choices=Role_choices, blank=True, null=True)
    catogry = models.CharField(max_length=50, choices=Catogry_choices, blank=True, null=True)
    
    class Meta:
        verbose_name = "Department Member"
        verbose_name_plural = "Department Members"

    def __str__(self):
        return f"{self.name} - {self.role}"
    


class SiteSetting(models.Model):
    SiteSettings = models.CharField(max_length=100, default="Site Settings", editable=False)
    maintenance_mode = models.BooleanField(default=False)
    max_students_per_batch = models.IntegerField("Max Students per Internship", default=3, help_text="Set the maximum number of students allowed per internship batch.")

    def __str__(self):
        return "Site Settings"

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"
        

class Announcement(models.Model):
    MESSAGE_COLOR_CHOICES = [
    ('green', 'Green'),
    ('orange', 'Orange'),
    ('red', 'Red'),
]
    message1 = models.TextField("Message 1", max_length=500, blank=True, null=True)
    is_message1_active = models.BooleanField("Show Message 1", default=False)
    message1_color = models.CharField("Message 1 Color", max_length=10, choices=MESSAGE_COLOR_CHOICES, default='green')


    message2 = models.TextField("Message 2", max_length=500, blank=True, null=True)
    is_message2_active = models.BooleanField("Show Message 2", default=False)
    message2_color = models.CharField("Message 2 Color", max_length=10, choices=MESSAGE_COLOR_CHOICES, default='orange')


    def __str__(self):
        return "Announcements"

    class Meta:
        verbose_name = "Site Announcement"
        verbose_name_plural = "Site Announcements"
        
        
class downloadable_files(models.Model):
    file_name = models.CharField(max_length=100, blank=True, null=True)
    file_link = models.URLField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return self.file_name
    
    class Meta:
        verbose_name = "Downloadable File"
        verbose_name_plural = "Downloadable Files"