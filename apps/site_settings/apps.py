from django.apps import AppConfig


class SiteSettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.site_settings'
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
