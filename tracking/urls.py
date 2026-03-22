from django.urls import path
from . import views

app_name = 'tracking'

urlpatterns = [
    # Vehicle Status
    path('vehicle-status/', views.vehicle_status_list, name='vehicle_status_list'),
    path('vehicle-status/<int:placement_pk>/leg-update/', views.leg_update, name='leg_update'),
    path('vehicle-status/<int:placement_pk>/leg/<int:leg_pk>/add-status/', views.add_leg_status, name='add_leg_status'),
    # POD
    path('pod/', views.pod_list, name='pod_list'),
    path('pod/<int:job_pk>/upload/', views.pod_upload, name='pod_upload'),
]
