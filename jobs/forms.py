from django import forms
from django.utils import timezone

from .models import JobOrder, JobCancellation
from masters.models import (
    Branch, Customer, ServiceRoute, Lane, Location,
    MaterialType, TruckType, FreightType, CancellationReason,
)


class SplitDateTimeWidget(forms.MultiWidget):
    """Custom widget that splits a DateTimeField into separate date and time inputs."""

    def __init__(self, attrs=None):
        date_attrs = {'type': 'date', 'class': 'form-control form-control-sm'}
        time_attrs = {'type': 'time', 'class': 'form-control form-control-sm'}
        if attrs:
            date_attrs.update(attrs)
            time_attrs.update(attrs)
        widgets = [
            forms.DateInput(attrs=date_attrs),
            forms.TimeInput(attrs=time_attrs),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            if isinstance(value, str):
                value = timezone.datetime.fromisoformat(value)
            return [value.date(), value.strftime('%H:%M')]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        vals = super().value_from_datadict(data, files, name)
        return vals


class SplitDateTimeField(forms.MultiValueField):
    """Field that combines separate date and time inputs into a datetime."""

    def __init__(self, **kwargs):
        fields = [
            forms.DateField(required=False),
            forms.TimeField(required=False),
        ]
        kwargs.setdefault('widget', SplitDateTimeWidget())
        kwargs.setdefault('required', False)
        super().__init__(fields=fields, **kwargs)

    def compress(self, data_list):
        if data_list and data_list[0] and data_list[1]:
            from datetime import datetime
            combined = datetime.combine(data_list[0], data_list[1])
            return timezone.make_aware(combined) if timezone.is_naive(combined) else combined
        if data_list and data_list[0]:
            from datetime import datetime, time
            combined = datetime.combine(data_list[0], time.min)
            return timezone.make_aware(combined) if timezone.is_naive(combined) else combined
        return None


BS_INPUT = {'class': 'form-control form-control-sm'}
BS_SELECT = {'class': 'form-select form-select-sm'}
BS_TEXTAREA = {'class': 'form-control form-control-sm', 'rows': 2}


class QuickLoadPostingForm(forms.ModelForm):
    reporting_datetime = SplitDateTimeField(required=False, label='Reporting Date / Time')
    cut_off_datetime = SplitDateTimeField(required=False, label='Cut Off Date / Time')
    do_validity_datetime = SplitDateTimeField(required=False, label='DO Validity Date / Time')

    class Meta:
        model = JobOrder
        fields = [
            'customer', 'customer_email', 'customer_contact_no',
            'customer_client', 'customer_job_no',
            'movement_type', 'movement_for', 'move_by',
            'service_type', 'service_route', 'lane',
            'origin', 'destination',
            'stuffing_point', 'stuffing_date',
            'material_type', 'truck_type', 'no_of_trailers',
            'gross_weight_mt',
            'freight_type', 'offered_freight_rate', 'adv_receipt_amount',
            'payment_day', 'load_preference',
            'reporting_datetime', 'cut_off_datetime', 'do_validity_datetime',
            'sales_person',
            'remarks', 'customer_expectation', 'cn_number',
        ]
        widgets = {
            'customer': forms.Select(attrs=BS_SELECT),
            'customer_email': forms.TextInput(attrs=BS_INPUT),
            'customer_contact_no': forms.TextInput(attrs=BS_INPUT),
            'customer_client': forms.TextInput(attrs=BS_INPUT),
            'customer_job_no': forms.TextInput(attrs=BS_INPUT),
            'movement_type': forms.Select(attrs=BS_SELECT),
            'movement_for': forms.Select(attrs=BS_SELECT),
            'move_by': forms.Select(attrs=BS_SELECT),
            'service_type': forms.Select(attrs=BS_SELECT),
            'service_route': forms.Select(attrs=BS_SELECT),
            'lane': forms.Select(attrs=BS_SELECT),
            'origin': forms.Select(attrs=BS_SELECT),
            'destination': forms.Select(attrs=BS_SELECT),
            'stuffing_point': forms.Select(attrs=BS_SELECT),
            'stuffing_date': forms.DateInput(attrs={**BS_INPUT, 'type': 'date'}),
            'material_type': forms.Select(attrs=BS_SELECT),
            'truck_type': forms.Select(attrs=BS_SELECT),
            'no_of_trailers': forms.NumberInput(attrs=BS_INPUT),
            'gross_weight_mt': forms.NumberInput(attrs={**BS_INPUT, 'step': '0.001'}),
            'freight_type': forms.Select(attrs=BS_SELECT),
            'offered_freight_rate': forms.NumberInput(attrs={**BS_INPUT, 'step': '0.01'}),
            'adv_receipt_amount': forms.NumberInput(attrs={**BS_INPUT, 'step': '0.01'}),
            'payment_day': forms.NumberInput(attrs=BS_INPUT),
            'load_preference': forms.Select(attrs=BS_SELECT),
            'sales_person': forms.Select(attrs=BS_SELECT),
            'remarks': forms.Textarea(attrs=BS_TEXTAREA),
            'customer_expectation': forms.Textarea(attrs=BS_TEXTAREA),
            'cn_number': forms.TextInput(attrs=BS_INPUT),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make only customer truly required at form level
        for field_name, field in self.fields.items():
            if field_name not in ('customer', 'movement_type'):
                field.required = False
        # Filter active items only
        self.fields['customer'].queryset = Customer.objects.filter(is_active=True)
        self.fields['service_route'].queryset = ServiceRoute.objects.filter(is_active=True)
        self.fields['lane'].queryset = Lane.objects.filter(is_active=True)
        self.fields['origin'].queryset = Location.objects.filter(is_active=True)
        self.fields['destination'].queryset = Location.objects.filter(is_active=True)
        self.fields['stuffing_point'].queryset = Location.objects.filter(is_active=True)
        self.fields['material_type'].queryset = MaterialType.objects.filter(is_active=True)
        self.fields['truck_type'].queryset = TruckType.objects.filter(is_active=True)
        self.fields['freight_type'].queryset = FreightType.objects.filter(is_active=True)


class JobCancellationForm(forms.ModelForm):
    class Meta:
        model = JobCancellation
        fields = ['reason', 'remarks']
        widgets = {
            'reason': forms.Select(attrs=BS_SELECT),
            'remarks': forms.Textarea(attrs={**BS_TEXTAREA, 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].queryset = CancellationReason.objects.filter(is_active=True)
