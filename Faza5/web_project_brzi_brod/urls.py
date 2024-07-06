# Andrej Ačković 0263/2021
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/doc/", include('django.contrib.admindocs.urls')),
    path("admin/", admin.site.urls),
    path("studassist/", include("studassist.urls")),
    path("", include("studassist.urls"))
]
