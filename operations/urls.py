from django.urls import path
from . import views

app_name = 'operations'

urlpatterns = [
    # Trailer Attendance
    path('trailer-attendance/', views.trailer_attendance, name='trailer_attendance'),
    # Planning
    path('planning/', views.planning_job_list, name='planning_job_list'),
    path('planning/<int:job_pk>/', views.planning_detail, name='planning_detail'),
    path('planning/<int:job_pk>/entry/', views.planning_entry, name='planning_entry'),
    path('planning/<int:job_pk>/entry/<int:pk>/edit/', views.planning_entry_edit, name='planning_entry_edit'),
    # Placement
    path('placement/', views.placement_job_list, name='placement_job_list'),
    path('placement/<int:job_pk>/', views.placement_detail, name='placement_detail'),
    path('placement/<int:job_pk>/entry/', views.placement_entry, name='placement_entry'),
    path('placement/<int:job_pk>/entry/<int:pk>/edit/', views.placement_entry_edit, name='placement_entry_edit'),
    # AJAX
    path('api/vehicles-by-vendor/<int:vendor_pk>/', views.vehicles_by_vendor, name='vehicles_by_vendor'),
    path('api/driver-by-mobile/', views.driver_by_mobile, name='driver_by_mobile'),
]
