import csv
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from .models import JobOrder, JobCancellation
from .forms import QuickLoadPostingForm, JobCancellationForm
from masters.models import Customer


@login_required
def dashboard(request):
    """Main dashboard with tabbed views: today_load, unconnected, connected."""
    branch = request.current_branch
    tab = request.GET.get('tab', 'today_load')
    today = timezone.localdate()

    if tab == 'unconnected':
        jobs = JobOrder.objects.filter(
            branch=branch, status=JobOrder.Status.POSTED
        ).select_related(
            'customer', 'service_route', 'truck_type', 'freight_type', 'posted_by'
        )
    elif tab == 'connected':
        jobs = JobOrder.objects.filter(
            branch=branch,
            status__in=[
                JobOrder.Status.PLANNED,
                JobOrder.Status.PLACED,
                JobOrder.Status.IN_PROGRESS,
            ]
        ).select_related(
            'customer', 'service_route', 'truck_type', 'freight_type', 'posted_by'
        )
    else:
        # Default: today_load
        jobs = JobOrder.objects.filter(
            branch=branch, job_date__date=today
        ).select_related(
            'customer', 'service_route', 'truck_type', 'freight_type', 'posted_by'
        )

    # Counts for tab badges
    today_count = JobOrder.objects.filter(branch=branch, job_date__date=today).count()
    unconnected_count = JobOrder.objects.filter(
        branch=branch, status=JobOrder.Status.POSTED
    ).count()
    connected_count = JobOrder.objects.filter(
        branch=branch,
        status__in=[
            JobOrder.Status.PLANNED,
            JobOrder.Status.PLACED,
            JobOrder.Status.IN_PROGRESS,
        ]
    ).count()

    context = {
        'jobs': jobs,
        'tab': tab,
        'today_count': today_count,
        'unconnected_count': unconnected_count,
        'connected_count': connected_count,
    }
    return render(request, 'jobs/dashboard.html', context)


@login_required
def quick_load_posting(request, pk=None):
    """Create or edit a job order via the quick load posting form."""
    branch = request.current_branch
    instance = None
    if pk:
        instance = get_object_or_404(JobOrder, pk=pk, branch=branch)

    if request.method == 'POST':
        form = QuickLoadPostingForm(request.POST, instance=instance)
        if form.is_valid():
            job = form.save(commit=False)
            job.branch = branch
            if not pk:
                job.posted_by = request.user
                job.status = JobOrder.Status.POSTED
            job.save()
            messages.success(request, f'Job Order {job.job_order_no} saved successfully.')
            return redirect('jobs:dashboard')
    else:
        form = QuickLoadPostingForm(instance=instance)

    context = {
        'form': form,
        'editing': pk is not None,
        'job': instance,
    }
    return render(request, 'jobs/quick_load_posting.html', context)


@login_required
def load_list(request):
    """Table of loads for the current branch."""
    branch = request.current_branch
    jobs = JobOrder.objects.filter(
        branch=branch
    ).exclude(
        status=JobOrder.Status.CANCELLED
    ).select_related(
        'service_route', 'material_type', 'truck_type', 'freight_type', 'posted_by'
    ).order_by('-job_date')

    context = {'jobs': jobs}
    return render(request, 'jobs/load_list.html', context)


@login_required
def job_detail(request, pk):
    """Detail view of a single job order."""
    job = get_object_or_404(
        JobOrder.objects.select_related(
            'branch', 'customer', 'service_route', 'lane',
            'origin', 'destination', 'stuffing_point',
            'material_type', 'truck_type', 'freight_type',
            'sales_person', 'posted_by',
        ),
        pk=pk
    )
    context = {'job': job}
    return render(request, 'jobs/job_detail.html', context)


@login_required
def cancel_job(request, pk):
    """Show cancellation form and cancel a job order."""
    branch = request.current_branch
    job = get_object_or_404(JobOrder, pk=pk, branch=branch)

    if job.status == JobOrder.Status.CANCELLED:
        messages.warning(request, 'This job is already cancelled.')
        return redirect('jobs:dashboard')

    if request.method == 'POST':
        form = JobCancellationForm(request.POST)
        if form.is_valid():
            cancellation = form.save(commit=False)
            cancellation.job_order = job
            cancellation.cancelled_by = request.user
            cancellation.save()
            job.status = JobOrder.Status.CANCELLED
            job.save(update_fields=['status', 'updated_at'])
            messages.success(request, f'Job Order {job.job_order_no} has been cancelled.')
            return redirect('jobs:dashboard')
    else:
        form = JobCancellationForm()

    context = {'form': form, 'job': job}
    return render(request, 'jobs/cancel_job.html', context)


@login_required
def unconnected_list(request):
    """List of POSTED jobs (unconnected) that can be cancelled."""
    branch = request.current_branch
    jobs = JobOrder.objects.filter(
        branch=branch, status=JobOrder.Status.POSTED
    ).select_related(
        'customer', 'service_route', 'truck_type', 'freight_type', 'posted_by'
    ).order_by('-job_date')

    context = {'jobs': jobs}
    return render(request, 'jobs/unconnected_list.html', context)


@login_required
def export_csv(request):
    """Export current dashboard data as CSV."""
    branch = request.current_branch
    tab = request.GET.get('tab', 'today_load')
    today = timezone.localdate()

    if tab == 'unconnected':
        jobs = JobOrder.objects.filter(branch=branch, status=JobOrder.Status.POSTED)
    elif tab == 'connected':
        jobs = JobOrder.objects.filter(
            branch=branch,
            status__in=[
                JobOrder.Status.PLANNED,
                JobOrder.Status.PLACED,
                JobOrder.Status.IN_PROGRESS,
            ]
        )
    else:
        jobs = JobOrder.objects.filter(branch=branch, job_date__date=today)

    jobs = jobs.select_related(
        'customer', 'service_route', 'truck_type', 'freight_type', 'posted_by'
    )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="job_orders_{tab}_{today}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Sr No', 'Job Order No', 'Job Date', 'Customer Name',
        'Movement Type', 'Route', 'Truck Type', 'Freight Type',
        'Freight Rate', 'Status', 'Posted By',
    ])

    for idx, job in enumerate(jobs, start=1):
        writer.writerow([
            idx,
            job.job_order_no,
            job.job_date.strftime('%d-%m-%Y %H:%M') if job.job_date else '',
            job.customer.name if job.customer else '',
            job.get_movement_type_display(),
            job.service_route.name if job.service_route else '',
            job.truck_type.name if job.truck_type else '',
            job.freight_type.name if job.freight_type else '',
            job.offered_freight_rate,
            job.get_status_display(),
            (job.posted_by.get_full_name() or job.posted_by.username) if job.posted_by else '',
        ])

    return response


@login_required
def customer_search_api(request):
    """AJAX endpoint returning matching customers as JSON."""
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    customers = Customer.objects.filter(
        Q(name__icontains=q) | Q(email__icontains=q),
        is_active=True,
    )[:20]

    results = [
        {
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'contact_no': c.contact_no,
        }
        for c in customers
    ]
    return JsonResponse({'results': results})
