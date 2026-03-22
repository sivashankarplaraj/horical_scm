from django.contrib import admin
from .models import TrailerAttendance, TrailerPlanning, TrailerPlacement


@admin.register(TrailerAttendance)
class TrailerAttendanceAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'vendor', 'no_running_from', 'reason_for_not_running', 'branch', 'created_at')
    list_filter = ('branch', 'vendor')
    search_fields = ('vehicle__vehicle_no', 'vendor__name')
    date_hierarchy = 'no_running_from'


@admin.register(TrailerPlanning)
class TrailerPlanningAdmin(admin.ModelAdmin):
    list_display = ('job_order', 'vendor', 'vehicle', 'exp_reporting_datetime', 'planned_by', 'planned_at')
    list_filter = ('branch', 'vendor')
    search_fields = ('job_order__job_order_no', 'vehicle__vehicle_no')
    raw_id_fields = ('job_order', 'vendor', 'vehicle')


@admin.register(TrailerPlacement)
class TrailerPlacementAdmin(admin.ModelAdmin):
    list_display = ('job_order', 'vendor', 'vehicle', 'reporting_datetime', 'driver_name', 'placed_at')
    list_filter = ('branch', 'vendor', 'tracking_through')
    search_fields = ('job_order__job_order_no', 'vehicle__vehicle_no', 'container_no_1', 'container_no_2')
    raw_id_fields = ('job_order', 'vendor', 'vehicle', 'planning')
