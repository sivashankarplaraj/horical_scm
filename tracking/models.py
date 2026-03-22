from django.db import models
from django.conf import settings


class VehicleLeg(models.Model):
    placement = models.ForeignKey(
        'operations.TrailerPlacement', on_delete=models.CASCADE, related_name='legs'
    )
    job_order = models.ForeignKey(
        'jobs.JobOrder', on_delete=models.CASCADE, related_name='legs'
    )
    leg_number = models.PositiveIntegerField()
    description = models.CharField(max_length=255)
    from_location = models.ForeignKey(
        'masters.Location', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='legs_from'
    )
    to_location = models.ForeignKey(
        'masters.Location', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='legs_to'
    )
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['placement', 'leg_number']
        unique_together = ['placement', 'leg_number']

    def __str__(self):
        return f"Leg {self.leg_number}: {self.description}"

    @property
    def latest_status(self):
        return self.status_updates.order_by('-status_datetime').first()


class LegStatusUpdate(models.Model):
    class Status(models.TextChoices):
        NOT_YET_START = 'NOT_YET_START', 'Not Yet Start'
        LOADING = 'LOADING', 'Loading'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        UNLOADING = 'UNLOADING', 'Unloading'
        WAITING_FOR_DOCUMENT = 'WAITING_DOC', 'Waiting For Document'
        WAITING_FOR_STUFFING = 'WAITING_STUFF', 'Waiting For Stuffing'
        WAITING_FOR_DESTUFFING = 'WAITING_DESTUFF', 'Waiting For De-Stuffing'
        REACHED = 'REACHED', 'Reached'
        OUT = 'OUT', 'Out'
        TRIP_STARTED = 'TRIP_STARTED', 'Trip Started'
        TRAILER_CHANGE = 'TRAILER_CHANGE', 'Trailer Change'
        DRIVER_CHANGE = 'DRIVER_CHANGE', 'Driver Change'
        MOBILE_CHANGE = 'MOBILE_CHANGE', 'Mobile Change'
        JOB_COMPLETED = 'JOB_COMPLETED', 'Job Completed'
        JOB_COMPLETED_NEXT_PNR = 'JOB_COMP_PNR', 'Job Completed – Next PNR Movement'

    leg = models.ForeignKey(VehicleLeg, on_delete=models.CASCADE, related_name='status_updates')
    status = models.CharField(max_length=20, choices=Status.choices)
    status_datetime = models.DateTimeField()
    remarks = models.TextField(blank=True)
    gps_location = models.CharField(max_length=255, blank=True)
    is_other_info = models.BooleanField(default=False)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-status_datetime']

    def __str__(self):
        return f"{self.leg} – {self.get_status_display()}"


class ProofOfDelivery(models.Model):
    class PODType(models.TextChoices):
        DIGITAL = 'DIGITAL', 'Digital POD'
        PHYSICAL = 'PHYSICAL', 'Physical POD'

    job_order = models.ForeignKey(
        'jobs.JobOrder', on_delete=models.CASCADE, related_name='pods'
    )
    placement = models.ForeignKey(
        'operations.TrailerPlacement', on_delete=models.CASCADE,
        null=True, blank=True, related_name='pods'
    )
    pod_type = models.CharField(max_length=10, choices=PODType.choices)
    file = models.FileField(upload_to='pods/%Y/%m/')
    delivery_date = models.DateField(null=True, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Proof of Delivery'
        verbose_name_plural = 'Proofs of Delivery'

    def __str__(self):
        return f"POD: {self.job_order.job_order_no}"
