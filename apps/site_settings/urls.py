from django.urls import path
from . import views
from .views import performance_view, downloadable_files_view


urlpatterns = [
    path('',views.home, name='home'),
    # path('sitelogin/', views.sitelogin, name='sitelogin'),
    # path('logout/', views.logout_view, name='logout'),

    path("server-stats/", performance_view, name="performance"),
    path("downloadable-files/", views.downloadable_files_view, name="downloadable_files"),


    
]


