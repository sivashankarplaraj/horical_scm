from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('masters/', include('masters.urls', namespace='masters')),
    path('jobs/', include('jobs.urls', namespace='jobs')),
    path('operations/', include('operations.urls', namespace='operations')),
    path('tracking/', include('tracking.urls', namespace='tracking')),
    path('', lambda r: redirect('jobs:dashboard'), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
