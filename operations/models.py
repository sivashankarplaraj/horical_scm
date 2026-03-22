from django.db import models
from django.conf import settings


class TrailerAttendance(models.Model):
    vendor = models.ForeignKey('masters.Vendor', on_delete=models.PROTECT)
    vehicle = models.ForeignKey('masters.Vehicle', on_delete=models.PROTECT)
    closing_kmr_hmr = models.CharField(max_length=30, blank=True)
    no_running_from = models.DateTimeField()
    alternate_vehicle_no = models.CharField(max_length=20, blank=True)
    reason_for_not_running = models.ForeignKey(
        'masters.NotRunningReason', on_delete=models.SET_NULL, null=True, blank=True
    )
    rent_applicable = models.BooleanField(default=False)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)
    branch = models.ForeignKey('masters.Branch', on_delete=models.PROTECT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Trailer Attendances'

    def __str__(self):
        return f"{self.vehicle.vehicle_no} - {self.no_running_from.date()}"


class TrailerPlanning(models.Model):
    job_order = models.ForeignKey('jobs.JobOrder', on_delete=models.CASCADE, related_name='plannings')
    vendor = models.ForeignKey('masters.Vendor', on_delete=models.PROTECT)
    vehicle = models.ForeignKey('masters.Vehicle', on_delete=models.PROTECT)
    customer_job_no = models.CharField(max_length=50, blank=True)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    exp_reporting_datetime = models.DateTimeField(null=True, blank=True)
    exp_trip_start_datetime = models.DateTimeField(null=True, blank=True)
    cut_off_datetime = models.DateTimeField(null=True, blank=True)
    do_validity_datetime = models.DateTimeField(null=True, blank=True)
    special_request = models.TextField(blank=True)
    branch = models.ForeignKey('masters.Branch', on_delete=models.PROTECT)
    planned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    planned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-planned_at']

    def __str__(self):
        return f"Plan: {self.job_order.job_order_no} → {self.vehicle.vehicle_no}"


class TrailerPlacement(models.Model):
    class LoadType(models.TextChoices):
        CARGO = 'CARGO', 'Cargo'
        CONTAINER = 'CONTAINER', 'Container'

    class TrackingThrough(models.TextChoices):
        ABR = 'ABR', 'ABR'
        INTUGINE = 'INTUGINE', 'Intugine'
        SIM = 'SIM', 'SIM Tracking'
        MANUAL = 'MANUAL', 'Manual'

    job_order = models.ForeignKey('jobs.JobOrder', on_delete=models.CASCADE, related_name='placements')
    planning = models.OneToOneField(
        TrailerPlanning, on_delete=models.SET_NULL, null=True, blank=True, related_name='placement'
    )
    vendor = models.ForeignKey('masters.Vendor', on_delete=models.PROTECT)
    vehicle = models.ForeignKey('masters.Vehicle', on_delete=models.PROTECT)

    # Schedule
    reporting_datetime = models.DateTimeField(null=True, blank=True)
    trip_start_datetime = models.DateTimeField(null=True, blank=True)
    exp_job_complete_datetime = models.DateTimeField(null=True, blank=True)
    cut_off_datetime = models.DateTimeField(null=True, blank=True)
    do_validity_datetime = models.DateTimeField(null=True, blank=True)

    # Trip
    trip_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    empty_running_kmr = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    veh_start_state = models.CharField(max_length=100, blank=True)
    veh_start_city = models.CharField(max_length=100, blank=True)

    # Driver
    driver = models.ForeignKey(
        'masters.Driver', on_delete=models.SET_NULL, null=True, blank=True
    )
    driver_mobile_no = models.CharField(max_length=15, blank=True)
    driver_name = models.CharField(max_length=100, blank=True)
    dl_no = models.CharField(max_length=30, blank=True)

    # Financials
    diesel_litres = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    diesel_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    diesel_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    trailer_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    trip_advance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    trip_incentive = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    customer_incentive = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Container / Cargo
    load_type = models.CharField(max_length=20, choices=LoadType.choices, blank=True)
    container_no_1 = models.CharField(max_length=20, blank=True)
    container_size_1 = models.CharField(max_length=5, blank=True)
    container_no_2 = models.CharField(max_length=20, blank=True)
    container_size_2 = models.CharField(max_length=5, blank=True)
    customer_job_no = models.CharField(max_length=50, blank=True)

    # Tracking
    engaged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='engaged_placements'
    )
    tracking_through = models.CharField(
        max_length=20, choices=TrackingThrough.choices, blank=True
    )
    remarks = models.TextField(blank=True)

    branch = models.ForeignKey('masters.Branch', on_delete=models.PROTECT)
    placed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='placed_placements'
    )
    placed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-placed_at']

    def __str__(self):
        return f"Placement: {self.job_order.job_order_no} → {self.vehicle.vehicle_no}"

    def save(self, *args, **kwargs):
        self.diesel_amount = self.diesel_litres * self.diesel_rate
        super().save(*args, **kwargs)
