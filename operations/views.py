from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages

from .models import TrailerAttendance, TrailerPlanning, TrailerPlacement
from .forms import TrailerAttendanceForm, TrailerPlanningEntryForm, TrailerPlacementEntryForm
from jobs.models import JobOrder
from masters.models import Vendor, Vehicle, Driver


def _branch(request):
    return getattr(request, 'current_branch', None)


# ── Trailer Attendance ──────────────────────────────────────────────────────

@login_required
def trailer_attendance(request):
    branch = _branch(request)
    if request.method == 'POST':
        form = TrailerAttendanceForm(request.POST)
        if form.is_valid():
            att = form.save(commit=False)
            att.branch = branch
            att.created_by = request.user
            att.save()
            messages.success(request, 'Trailer attendance entry saved.')
            return redirect('operations:trailer_attendance')
    else:
        form = TrailerAttendanceForm()
    return render(request, 'operations/trailer_attendance.html', {'form': form})


# ── Trailer Planning ────────────────────────────────────────────────────────

@login_required
def planning_job_list(request):
    branch = _branch(request)
    q = request.GET.get('q', '')
    jobs = JobOrder.objects.filter(
        branch=branch, status=JobOrder.Status.POSTED
    ).select_related('customer', 'truck_type', 'service_route')
    if q:
        jobs = jobs.filter(job_order_no__icontains=q)
    return render(request, 'operations/planning_job_list.html', {'jobs': jobs, 'q': q})


@login_required
def planning_detail(request, job_pk):
    branch = _branch(request)
    job = get_object_or_404(JobOrder, pk=job_pk, branch=branch)

    vendors = (
        Vendor.objects.filter(is_active=True)
        .prefetch_related('vehicles__truck_type')
        .order_by('name')
    )

    in_transit_ids = set(
        TrailerPlacement.objects.filter(
            job_order__status=JobOrder.Status.IN_PROGRESS
        ).values_list('vehicle_id', flat=True)
    )
    planned_ids = set(
        TrailerPlanning.objects.filter(
            job_order__status=JobOrder.Status.PLANNED
        ).values_list('vehicle_id', flat=True)
    )

    vendor_cards = []
    for vendor in vendors:
        veh_list = []
        for v in vendor.vehicles.filter(is_active=True):
            if v.id in in_transit_ids:
                status = 'in_transit'
            elif v.id in planned_ids:
                status = 'planned'
            else:
                status = 'available'
            veh_list.append({'vehicle': v, 'status': status})
        if veh_list:
            vendor_cards.append({'vendor': vendor, 'vehicles': veh_list})

    return render(request, 'operations/planning_detail.html', {
        'job': job, 'vendor_cards': vendor_cards,
    })


@login_required
def planning_entry(request, job_pk):
    branch = _branch(request)
    job = get_object_or_404(JobOrder, pk=job_pk, branch=branch)
    initial = {}
    for key, model in [('vendor', Vendor), ('vehicle', Vehicle)]:
        pk_val = request.GET.get(key)
        if pk_val:
            try:
                initial[key] = model.objects.get(pk=pk_val)
            except model.DoesNotExist:
                pass

    if request.method == 'POST':
        form = TrailerPlanningEntryForm(request.POST)
        if form.is_valid():
            planning = form.save(commit=False)
            planning.job_order = job
            planning.branch = branch
            planning.planned_by = request.user
            planning.save()
            job.status = JobOrder.Status.PLANNED
            job.save(update_fields=['status', 'updated_at'])
            messages.success(request, f'Planning entry saved for {job.job_order_no}.')
            return redirect('operations:planning_job_list')
    else:
        form = TrailerPlanningEntryForm(initial=initial)

    return render(request, 'operations/planning_entry.html', {'form': form, 'job': job})


@login_required
def planning_entry_edit(request, job_pk, pk):
    branch = _branch(request)
    job = get_object_or_404(JobOrder, pk=job_pk, branch=branch)
    planning = get_object_or_404(TrailerPlanning, pk=pk, job_order=job)
    if request.method == 'POST':
        form = TrailerPlanningEntryForm(request.POST, instance=planning)
        if form.is_valid():
            form.save()
            messages.success(request, 'Planning entry updated.')
            return redirect('operations:planning_job_list')
    else:
        form = TrailerPlanningEntryForm(instance=planning)
    return render(request, 'operations/planning_entry.html', {
        'form': form, 'job': job, 'editing': True
    })


# ── Trailer Placement ───────────────────────────────────────────────────────

@login_required
def placement_job_list(request):
    branch = _branch(request)
    q = request.GET.get('q', '')
    jobs = JobOrder.objects.filter(
        branch=branch, status=JobOrder.Status.PLANNED
    ).select_related('customer', 'truck_type', 'service_route')
    if q:
        jobs = jobs.filter(job_order_no__icontains=q)
    return render(request, 'operations/placement_job_list.html', {'jobs': jobs, 'q': q})


@login_required
def placement_detail(request, job_pk):
    branch = _branch(request)
    job = get_object_or_404(JobOrder, pk=job_pk, branch=branch)

    vendors = (
        Vendor.objects.filter(is_active=True)
        .prefetch_related('vehicles__truck_type')
        .order_by('name')
    )
    in_transit_ids = set(
        TrailerPlacement.objects.filter(
            job_order__status=JobOrder.Status.IN_PROGRESS
        ).values_list('vehicle_id', flat=True)
    )
    planned_ids = set(
        TrailerPlanning.objects.filter(
            job_order__status=JobOrder.Status.PLANNED
        ).values_list('vehicle_id', flat=True)
    )
    vendor_cards = []
    for vendor in vendors:
        veh_list = []
        for v in vendor.vehicles.filter(is_active=True):
            if v.id in in_transit_ids:
                status = 'in_transit'
            elif v.id in planned_ids:
                status = 'planned'
            else:
                status = 'available'
            veh_list.append({'vehicle': v, 'status': status})
        if veh_list:
            vendor_cards.append({'vendor': vendor, 'vehicles': veh_list})

    planning = TrailerPlanning.objects.filter(job_order=job).first()
    return render(request, 'operations/placement_detail.html', {
        'job': job, 'vendor_cards': vendor_cards, 'planning': planning,
    })


@login_required
def placement_entry(request, job_pk):
    branch = _branch(request)
    job = get_object_or_404(JobOrder, pk=job_pk, branch=branch)
    planning = TrailerPlanning.objects.filter(job_order=job).first()

    initial = {}
    if planning:
        initial['vendor'] = planning.vendor
        initial['vehicle'] = planning.vehicle
        if planning.exp_reporting_datetime:
            initial['reporting_datetime'] = planning.exp_reporting_datetime
    for key, model in [('vendor', Vendor), ('vehicle', Vehicle)]:
        pk_val = request.GET.get(key)
        if pk_val and not initial.get(key):
            try:
                initial[key] = model.objects.get(pk=pk_val)
            except model.DoesNotExist:
                pass

    if request.method == 'POST':
        form = TrailerPlacementEntryForm(request.POST)
        if form.is_valid():
            placement = form.save(commit=False)
            placement.job_order = job
            placement.planning = planning
            placement.branch = branch
            placement.placed_by = request.user
            placement.save()
            _generate_legs(placement)
            job.status = JobOrder.Status.PLACED
            job.save(update_fields=['status', 'updated_at'])
            messages.success(request, f'Placement entry saved for {job.job_order_no}.')
            return redirect('tracking:vehicle_status_list')
    else:
        form = TrailerPlacementEntryForm(initial=initial)

    return render(request, 'operations/placement_entry.html', {
        'form': form, 'job': job, 'planning': planning
    })


@login_required
def placement_entry_edit(request, job_pk, pk):
    branch = _branch(request)
    job = get_object_or_404(JobOrder, pk=job_pk, branch=branch)
    placement = get_object_or_404(TrailerPlacement, pk=pk, job_order=job)
    if request.method == 'POST':
        form = TrailerPlacementEntryForm(request.POST, instance=placement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Placement entry updated.')
            return redirect('operations:placement_job_list')
    else:
        form = TrailerPlacementEntryForm(instance=placement)
    return render(request, 'operations/placement_entry.html', {
        'form': form, 'job': job, 'editing': True
    })


def _generate_legs(placement):
    from tracking.models import VehicleLeg
    job = placement.job_order
    if not job.service_route:
        VehicleLeg.objects.create(
            placement=placement, job_order=job, leg_number=1,
            description=(
                f"{job.origin} to {job.destination}"
                if job.origin and job.destination else "Leg 1"
            ),
            from_location=job.origin, to_location=job.destination, is_current=True,
        )
        return
    for i, leg in enumerate(job.service_route.legs.order_by('leg_number')):
        VehicleLeg.objects.create(
            placement=placement, job_order=job,
            leg_number=leg.leg_number,
            description=leg.description or f"Leg {leg.leg_number}",
            is_current=(i == 0),
        )


# ── AJAX ────────────────────────────────────────────────────────────────────

@login_required
def vehicles_by_vendor(request, vendor_pk):
    vehicles = Vehicle.objects.filter(
        vendor_id=vendor_pk, is_active=True
    ).select_related('truck_type').order_by('vehicle_no')
    return JsonResponse({
        'vehicles': [
            {'id': v.id, 'vehicle_no': v.vehicle_no, 'truck_type': v.truck_type.name}
            for v in vehicles
        ]
    })


@login_required
def driver_by_mobile(request):
    mobile = request.GET.get('mobile', '').strip()
    try:
        d = Driver.objects.get(mobile_no=mobile, is_active=True)
        return JsonResponse({'found': True, 'name': d.name, 'dl_no': d.dl_no, 'id': d.id})
    except Driver.DoesNotExist:
        return JsonResponse({'found': False})
