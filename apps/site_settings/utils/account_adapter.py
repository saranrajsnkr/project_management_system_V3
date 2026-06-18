# from allauth.account.adapter import DefaultAccountAdapter
# from django.shortcuts import redirect

# class CustomAccountAdapter(DefaultAccountAdapter):
#     def get_login_redirect_url(self, request):
#         return '/'

#     def get_login_url(self, request):
#         return '/login/'   # redirect to your site_login.html




from allauth.account.adapter import DefaultAccountAdapter
from django.contrib import messages
from django.core.exceptions import ValidationError


# class CustomAccountAdapter(DefaultAccountAdapter):
#     def is_open_for_signup(self, request):
#         return True

#     def clean_email(self, email):
#         """Restrict signup to only @veltech.edu.in emails"""
#         email = super().clean_email(email)
#         if not email.endswith("@veltech.edu.in"):
#             # Store the message so your template can catch it
#             request = self.request
#             if request:
#                 messages.add_message(
#                     request,
#                     messages.ERROR,
#                     "Please use your @veltech.edu.in email to sign up.",
#                     extra_tags='domain_error'
#                 )
#             # Prevent user creation
#             raise ValidationError("Only @veltech.edu.in emails are allowed.")
#         return email

#     def get_login_redirect_url(self, request):
#         return '/'

#     def get_login_url(self, request):
#         return '/login/'





# class CustomAccountAdapter(DefaultAccountAdapter):
#     def is_open_for_signup(self, request):
#         # Always allow signups (we will restrict by email later)
#         return True

#     def clean_email(self, email):
#         """Ensure only @veltech.edu.in emails can register via Google"""
#         email = super().clean_email(email)
#         if not email.endswith("@veltech.edu.in"):
#             raise ValidationError("Only @veltech.edu.in emails are allowed.")
#         return email

#     def get_login_redirect_url(self, request):
#         return '/'

#     def get_login_url(self, request):
#         return '/login/'




from django.core.exceptions import ValidationError
from django.contrib import messages
from apps.site_settings.models import dept_member

class CustomAccountAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        email = super().clean_email(email)
        request = getattr(self, 'request', None)

        # 🔹 1. Check domain
        if not email.endswith("@veltech.edu.in"):
            if request:
                messages.error(request, "Please use your @veltech.edu.in email to sign up.", extra_tags='domain_error')
            raise ValidationError("Only @veltech.edu.in emails are allowed.")

        # # 🔹 2. Check AIML dept membership
        # if not dept_member.objects.filter(email__iexact=email).exists():
        #     if request:
        #         messages.error(request, "Only AIML department members can sign up.", extra_tags='domain_error')
        #     raise ValidationError('Email not in AIML department.')

        return email

