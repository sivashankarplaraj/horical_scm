from django.db import models
from django.conf import settings


class JobOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        POSTED = 'POSTED', 'Posted'
        PLANNED = 'PLANNED', 'Planned'
        PLACED = 'PLACED', 'Placed'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        POD_PENDING = 'POD_PENDING', 'POD Pending'
        BILLED = 'BILLED', 'Billed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class MovementType(models.TextChoices):
        EXPORT = 'EXPORT', 'Export'
        IMPORT = 'IMPORT', 'Import'
        EMPTY = 'EMPTY', 'Empty'
        LOCAL = 'LOCAL', 'Local'

    class MovementFor(models.TextChoices):
        CALYX = 'CALYX', 'HORICAL'
        OTHER = 'OTHER', 'Other'

    class MoveBy(models.TextChoices):
        ON_WHEEL = 'ON_WHEEL', 'SCS'
        LCL = 'LCL', 'CFS'

    class ServiceType(models.TextChoices):
        LOCAL = 'LOCAL', 'Local'
        EXIM = 'EXIM', 'EXIM'
        LONG_HAUL = 'LONG_HAUL', 'Long Haul'

    class LoadPreference(models.TextChoices):
        ONE_TIME = 'ONE_TIME', 'One Time'
        REGULAR = 'REGULAR', 'Regular'

    MOVEMENT_PREFIX_MAP = {
        'EXPORT': 'EXP',
        'IMPORT': 'IMP',
        'EMPTY': 'MTY',
        'LOCAL': 'LOC',
    }

    # Auto-generated job order number
    job_order_no = models.CharField(max_length=30, unique=True, editable=False)

    branch = models.ForeignKey(
        'masters.Branch', on_delete=models.PROTECT, related_name='job_orders'
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    job_date = models.DateTimeField(auto_now_add=True)

    # Customer details
    customer = models.ForeignKey(
        'masters.Customer', on_delete=models.PROTECT, related_name='job_orders'
    )
    customer_email = models.CharField(max_length=200, blank=True)
    customer_contact_no = models.CharField(max_length=20, blank=True)
    customer_client = models.CharField(max_length=200, blank=True)
    customer_job_no = models.CharField(max_length=50, blank=True)

    # Movement info
    movement_type = models.CharField(
        max_length=10, choices=MovementType.choices, default=MovementType.EXPORT
    )
    movement_for = models.CharField(
        max_length=10, choices=MovementFor.choices, default=MovementFor.CALYX
    )
    move_by = models.CharField(
        max_length=10, choices=MoveBy.choices, default=MoveBy.ON_WHEEL
    )
    service_type = models.CharField(
        max_length=15, choices=ServiceType.choices, default=ServiceType.LOCAL
    )

    # Route / Lane / Locations
    service_route = models.ForeignKey(
        'masters.ServiceRoute', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='job_orders'
    )
    lane = models.ForeignKey(
        'masters.Lane', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='job_orders'
    )
    origin = models.ForeignKey(
        'masters.Location', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='job_orders_origin'
    )
    destination = models.ForeignKey(
        'masters.Location', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='job_orders_destination'
    )

    # Stuffing
    stuffing_point = models.ForeignKey(
        'masters.Location', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='job_orders_stuffing'
    )
    stuffing_date = models.DateField(null=True, blank=True)

    # Cargo / Truck
    material_type = models.ForeignKey(
        'masters.MaterialType', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='job_orders'
    )
    truck_type = models.ForeignKey(
        'masters.TruckType', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='job_orders'
    )
    no_of_trailers = models.PositiveIntegerField(default=1)
    gross_weight_mt = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True
    )

    # Freight / Payment
    freight_type = models.ForeignKey(
        'masters.FreightType', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='job_orders'
    )
    offered_freight_rate = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    adv_receipt_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    payment_day = models.PositiveIntegerField(default=0)

    load_preference = models.CharField(
        max_length=10, choices=LoadPreference.choices, default=LoadPreference.ONE_TIME
    )

    # Datetime milestones
    reporting_datetime = models.DateTimeField(null=True, blank=True)
    cut_off_datetime = models.DateTimeField(null=True, blank=True)
    do_validity_datetime = models.DateTimeField(null=True, blank=True)

    # People
    sales_person = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sales_job_orders'
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='posted_job_orders'
    )

    # Misc
    remarks = models.TextField(blank=True)
    customer_expectation = models.TextField(blank=True)
    cn_number = models.CharField(max_length=50, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-job_date']
        verbose_name = 'Job Order'
        verbose_name_plural = 'Job Orders'

    def __str__(self):
        return self.job_order_no

    @staticmethod
    def _get_financial_year(dt):
        """Return financial year string like '25-26' for a given date."""
        year = dt.year
        month = dt.month
        if month >= 4:
            fy_start = year
        else:
            fy_start = year - 1
        fy_end = fy_start + 1
        return f"{fy_start % 100:02d}-{fy_end % 100:02d}"

    def save(self, *args, **kwargs):
        if not self.job_order_no:
            from django.utils import timezone
            now = timezone.now()
            fy = self._get_financial_year(now)
            prefix = self.MOVEMENT_PREFIX_MAP.get(self.movement_type, 'EXP')

            # Determine next sequence number for this prefix and FY
            fy_suffix = f"/{fy}"
            prefix_pattern = f"{prefix}/J/"
            last_job = (
                JobOrder.objects
                .filter(job_order_no__startswith=prefix_pattern,
                        job_order_no__endswith=fy_suffix)
                .order_by('-job_order_no')
                .first()
            )
            if last_job:
                try:
                    # Extract sequence: EXP/J/000001/25-26 -> 000001
                    parts = last_job.job_order_no.split('/')
                    last_seq = int(parts[2])
                except (IndexError, ValueError):
                    last_seq = 0
            else:
                last_seq = 0

            new_seq = last_seq + 1
            self.job_order_no = f"{prefix}/J/{new_seq:06d}/{fy}"

        super().save(*args, **kwargs)


class JobCancellation(models.Model):
    job_order = models.OneToOneField(
        JobOrder, on_delete=models.CASCADE, related_name='cancellation'
    )
    reason = models.ForeignKey(
        'masters.CancellationReason', on_delete=models.PROTECT
    )
    remarks = models.TextField(blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    cancelled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Job Cancellation'
        verbose_name_plural = 'Job Cancellations'

    def __str__(self):
        return f"Cancellation: {self.job_order.job_order_no}"
