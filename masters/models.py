from django.db import models


class Branch(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=150)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_name']
        verbose_name_plural = 'branches'

    def __str__(self):
        return self.display_name


class Location(models.Model):
    class LocationType(models.TextChoices):
        PORT = 'PORT', 'Port'
        CFS = 'CFS', 'CFS'
        MTY = 'MTY', 'Empty Yard (MTY)'
        LOC = 'LOC', 'Local Location'
        CITY = 'CITY', 'City'

    name = models.CharField(max_length=200)
    location_type = models.CharField(max_length=10, choices=LocationType.choices)
    code = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_location_type_display()})"


class Lane(models.Model):
    name = models.CharField(max_length=255)
    origin = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='lanes_from')
    destination = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='lanes_to')
    estimated_distance_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ServiceRoute(models.Model):
    name = models.CharField(max_length=200)
    service_type = models.CharField(max_length=20, choices=[
        ('LOCAL', 'Local'), ('EXIM', 'EXIM'), ('LONG_HAUL', 'Long Haul')
    ])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ServiceRouteLeg(models.Model):
    service_route = models.ForeignKey(ServiceRoute, on_delete=models.CASCADE, related_name='legs')
    leg_number = models.PositiveIntegerField()
    from_location_type = models.CharField(max_length=10, choices=Location.LocationType.choices)
    to_location_type = models.CharField(max_length=10, choices=Location.LocationType.choices)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['service_route', 'leg_number']
        unique_together = ['service_route', 'leg_number']


class Vendor(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    pan_number = models.CharField(max_length=20, blank=True)
    gst_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='vendors', null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TruckType(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    class VehicleCategory(models.TextChoices):
        CONTRACTUAL = 'Contractual', 'Contractual'
        MARKET = 'Market', 'Market'

    vehicle_no = models.CharField(max_length=20, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='vehicles')
    truck_type = models.ForeignKey(TruckType, on_delete=models.PROTECT)
    category = models.CharField(max_length=20, choices=VehicleCategory.choices, default=VehicleCategory.CONTRACTUAL)
    gps_provider = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    current_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    last_gps_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    last_gps_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    last_gps_update = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['vehicle_no']

    def __str__(self):
        return self.vehicle_no


class Driver(models.Model):
    name = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=15)
    dl_no = models.CharField(max_length=30, blank=True, verbose_name="Driving License No")
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='drivers', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.mobile_no})"


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    contact_no = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    gst_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class MaterialType(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class FreightType(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CancellationReason(models.Model):
    reason = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.reason


class NotRunningReason(models.Model):
    reason = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.reason
