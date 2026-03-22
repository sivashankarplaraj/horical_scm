from django.contrib import admin
from .models import VehicleLeg, LegStatusUpdate, ProofOfDelivery


class LegStatusInline(admin.TabularInline):
    model = LegStatusUpdate
    extra = 0
    readonly_fields = ('created_at',)
    ordering = ('-status_datetime',)


@admin.register(VehicleLeg)
class VehicleLegAdmin(admin.ModelAdmin):
    list_display = ('placement', 'leg_number', 'description', 'is_current')
    search_fields = ('placement__job_order__job_order_no', 'description')
    inlines = [LegStatusInline]


@admin.register(LegStatusUpdate)
class LegStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ('leg', 'status', 'status_datetime', 'updated_by', 'created_at')
    list_filter = ('status',)
    search_fields = ('leg__placement__job_order__job_order_no',)


@admin.register(ProofOfDelivery)
class ProofOfDeliveryAdmin(admin.ModelAdmin):
    list_display = ('job_order', 'pod_type', 'delivery_date', 'uploaded_by', 'uploaded_at')
    list_filter = ('pod_type',)
    search_fields = ('job_order__job_order_no',)
    readonly_fields = ('uploaded_at',)
