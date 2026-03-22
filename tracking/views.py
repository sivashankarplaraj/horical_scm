from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from .models import VehicleLeg, LegStatusUpdate, ProofOfDelivery
from .forms import LegStatusUpdateForm, PODUploadForm
from operations.models import TrailerPlacement
from jobs.models import JobOrder


def _branch(request):
    return getattr(request, 'current_branch', None)


@login_required
def vehicle_status_list(request):
    branch = _branch(request)
    tab = request.GET.get('tab', 'domestic')
    q = request.GET.get('q', '')

    placements = TrailerPlacement.objects.filter(
        branch=branch,
        job_order__status__in=[JobOrder.Status.PLACED, JobOrder.Status.IN_PROGRESS]
    ).select_related(
        'job_order__customer', 'job_order__service_route',
        'vehicle__truck_type', 'vendor'
    ).order_by('-placed_at')

    if tab == 'container':
        placements = placements.filter(load_type='CONTAINER')
    else:
        placements = placements.exclude(load_type='CONTAINER')

    if q:
        placements = placements.filter(
            job_order__job_order_no__icontains=q
        )

    return render(request, 'tracking/vehicle_status_list.html', {
        'placements': placements,
        'tab': tab,
        'q': q,
    })


@login_required
def leg_update(request, placement_pk):
    branch = _branch(request)
    placement = get_object_or_404(TrailerPlacement, pk=placement_pk, branch=branch)
    legs = placement.legs.prefetch_related('status_updates').order_by('leg_number')

    return render(request, 'tracking/leg_update.html', {
        'placement': placement,
        'job': placement.job_order,
        'legs': legs,
        'status_form': LegStatusUpdateForm(),
    })


@login_required
def add_leg_status(request, placement_pk, leg_pk):
    branch = _branch(request)
    placement = get_object_or_404(TrailerPlacement, pk=placement_pk, branch=branch)
    leg = get_object_or_404(VehicleLeg, pk=leg_pk, placement=placement)

    if request.method == 'POST':
        form = LegStatusUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.leg = leg
            update.updated_by = request.user
            update.save()

            job = placement.job_order

            if update.status == LegStatusUpdate.Status.JOB_COMPLETED:
                job.status = JobOrder.Status.POD_PENDING
                job.save(update_fields=['status', 'updated_at'])
                messages.success(request, f'Job {job.job_order_no} marked completed. Awaiting POD.')
                return redirect('tracking:pod_list')

            elif update.status == LegStatusUpdate.Status.TRAILER_CHANGE:
                # Reset to placed so a new placement can be created
                job.status = JobOrder.Status.PLANNED
                job.save(update_fields=['status', 'updated_at'])
                messages.info(request, 'Trailer change recorded. Please create a new placement.')
                return redirect('operations:placement_job_list')

            else:
                if job.status == JobOrder.Status.PLACED:
                    job.status = JobOrder.Status.IN_PROGRESS
                    job.save(update_fields=['status', 'updated_at'])

            messages.success(request, 'Status updated.')
            return redirect('tracking:leg_update', placement_pk=placement_pk)
    else:
        form = LegStatusUpdateForm()

    legs = placement.legs.prefetch_related('status_updates').order_by('leg_number')
    return render(request, 'tracking/leg_update.html', {
        'placement': placement,
        'job': placement.job_order,
        'legs': legs,
        'status_form': form,
        'active_leg': leg,
    })


@login_required
def pod_list(request):
    branch = _branch(request)
    q = request.GET.get('q', '')
    jobs = JobOrder.objects.filter(
        branch=branch, status=JobOrder.Status.POD_PENDING
    ).select_related('customer').order_by('-updated_at')
    if q:
        jobs = jobs.filter(job_order_no__icontains=q)
    return render(request, 'tracking/pod_list.html', {'jobs': jobs, 'q': q})


@login_required
def pod_upload(request, job_pk):
    branch = _branch(request)
    job = get_object_or_404(JobOrder, pk=job_pk, branch=branch)
    placement = job.placements.order_by('-placed_at').first()

    if request.method == 'POST':
        form = PODUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pod = form.save(commit=False)
            pod.job_order = job
            pod.placement = placement
            pod.uploaded_by = request.user
            pod.save()
            job.status = JobOrder.Status.BILLED
            job.save(update_fields=['status', 'updated_at'])
            messages.success(request, f'POD uploaded for {job.job_order_no}. Job moved to Billing.')
            return redirect('tracking:pod_list')
    else:
        form = PODUploadForm()

    return render(request, 'tracking/pod_upload.html', {'form': form, 'job': job})
