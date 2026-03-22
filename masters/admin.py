from django.contrib import admin

from .models import (
    Branch,
    CancellationReason,
    Customer,
    Driver,
    FreightType,
    Lane,
    Location,
    MaterialType,
    NotRunningReason,
    ServiceRoute,
    ServiceRouteLeg,
    TruckType,
    Vehicle,
    Vendor,
)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('code', 'display_name', 'is_active')
    search_fields = ('name', 'code', 'display_name')
    list_filter = ('is_active',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_type', 'city', 'code', 'is_active')
    search_fields = ('name', 'code', 'city')
    list_filter = ('location_type', 'is_active')


@admin.register(Lane)
class LaneAdmin(admin.ModelAdmin):
    list_display = ('name', 'origin', 'location_1', 'location_2', 'destination', 'estimated_distance_km', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    raw_id_fields = ('origin', 'location_1', 'location_2', 'destination')


class ServiceRouteLegInline(admin.TabularInline):
    model = ServiceRouteLeg
    extra = 1
    ordering = ('leg_number',)


@admin.register(ServiceRoute)
class ServiceRouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'is_active')
    search_fields = ('name',)
    list_filter = ('service_type', 'is_active')
    inlines = [ServiceRouteLegInline]


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'branch', 'is_active')
    search_fields = ('name', 'phone', 'contact_person', 'gst_number')
    list_filter = ('is_active', 'branch')
    raw_id_fields = ('branch',)


@admin.register(TruckType)
class TruckTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_no', 'vendor', 'truck_type', 'category', 'is_active')
    search_fields = ('vehicle_no', 'vendor__name')
    list_filter = ('category', 'truck_type', 'is_active')
    raw_id_fields = ('vendor', 'current_location')


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile_no', 'dl_no', 'vendor', 'is_active')
    search_fields = ('name', 'mobile_no', 'dl_no')
    list_filter = ('is_active',)
    raw_id_fields = ('vendor',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact_no', 'is_active')
    search_fields = ('name', 'email', 'gst_number')
    list_filter = ('is_active',)


@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)


@admin.register(FreightType)
class FreightTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)


@admin.register(CancellationReason)
class CancellationReasonAdmin(admin.ModelAdmin):
    list_display = ('reason', 'is_active')
    search_fields = ('reason',)
    list_filter = ('is_active',)


@admin.register(NotRunningReason)
class NotRunningReasonAdmin(admin.ModelAdmin):
    list_display = ('reason', 'is_active')
    search_fields = ('reason',)
    list_filter = ('is_active',)
