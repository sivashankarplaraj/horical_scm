from django import forms
from django.utils import timezone

from .models import TrailerAttendance, TrailerPlanning, TrailerPlacement
from masters.models import Vendor, Vehicle, Driver, NotRunningReason

BS = {'class': 'form-control form-control-sm'}
SEL = {'class': 'form-select form-select-sm'}
TA = {'class': 'form-control form-control-sm', 'rows': 2}
DT_DATE = {'type': 'date', **BS}
DT_TIME = {'type': 'time', **BS}


class SplitDTWidget(forms.MultiWidget):
    def __init__(self):
        super().__init__([forms.DateInput(attrs=DT_DATE), forms.TimeInput(attrs=DT_TIME)])

    def decompress(self, value):
        if value:
            if hasattr(value, 'date'):
                return [value.date(), value.strftime('%H:%M')]
        return [None, None]


class SplitDTField(forms.MultiValueField):
    def __init__(self, **kwargs):
        kwargs.setdefault('required', False)
        kwargs.setdefault('widget', SplitDTWidget())
        super().__init__(
            fields=[forms.DateField(required=False), forms.TimeField(required=False)],
            **kwargs
        )

    def compress(self, data_list):
        if data_list and data_list[0] and data_list[1]:
            from datetime import datetime
            dt = datetime.combine(data_list[0], data_list[1])
            return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
        if data_list and data_list[0]:
            from datetime import datetime, time
            dt = datetime.combine(data_list[0], time.min)
            return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
        return None


class TrailerAttendanceForm(forms.ModelForm):
    no_running_from = SplitDTField(label='No Running From Date Time')

    class Meta:
        model = TrailerAttendance
        fields = [
            'vendor', 'vehicle', 'closing_kmr_hmr',
            'no_running_from', 'alternate_vehicle_no',
            'reason_for_not_running', 'rent_applicable', 'rent_amount', 'remarks',
        ]
        widgets = {
            'vendor': forms.Select(attrs=SEL),
            'vehicle': forms.Select(attrs=SEL),
            'closing_kmr_hmr': forms.TextInput(attrs=BS),
            'alternate_vehicle_no': forms.TextInput(attrs=BS),
            'reason_for_not_running': forms.Select(attrs=SEL),
            'rent_applicable': forms.Select(
                choices=[(False, 'No'), (True, 'Yes')], attrs=SEL
            ),
            'rent_amount': forms.NumberInput(attrs=BS),
            'remarks': forms.Textarea(attrs=TA),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor'].queryset = Vendor.objects.filter(is_active=True)
        self.fields['vehicle'].queryset = Vehicle.objects.filter(is_active=True)
        self.fields['reason_for_not_running'].queryset = NotRunningReason.objects.filter(is_active=True)
        for f in ['closing_kmr_hmr', 'alternate_vehicle_no', 'reason_for_not_running',
                  'rent_applicable', 'rent_amount', 'remarks']:
            self.fields[f].required = False


class TrailerPlanningEntryForm(forms.ModelForm):
    exp_reporting_datetime = SplitDTField(label='Exp Reporting Date/Time')
    exp_trip_start_datetime = SplitDTField(label='Exp Trip Start Date/Time')
    cut_off_datetime = SplitDTField(label='Cut Off Date/Time')
    do_validity_datetime = SplitDTField(label='DO Validity Date/Time')

    class Meta:
        model = TrailerPlanning
        fields = [
            'vendor', 'vehicle', 'customer_job_no', 'revenue',
            'exp_reporting_datetime', 'exp_trip_start_datetime',
            'cut_off_datetime', 'do_validity_datetime', 'special_request',
        ]
        widgets = {
            'vendor': forms.Select(attrs=SEL),
            'vehicle': forms.Select(attrs=SEL),
            'customer_job_no': forms.TextInput(attrs=BS),
            'revenue': forms.NumberInput(attrs={**BS, 'step': '0.01'}),
            'special_request': forms.Textarea(attrs=TA),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor'].queryset = Vendor.objects.filter(is_active=True)
        self.fields['vehicle'].queryset = Vehicle.objects.filter(is_active=True)
        for f in ['customer_job_no', 'revenue', 'special_request']:
            self.fields[f].required = False


class TrailerPlacementEntryForm(forms.ModelForm):
    reporting_datetime = SplitDTField(label='Reporting Date/Time')
    trip_start_datetime = SplitDTField(label='Trip Start Date/Time')
    exp_job_complete_datetime = SplitDTField(label='Exp Job Complete Date/Time')
    cut_off_datetime = SplitDTField(label='Cut Off Date/Time')
    do_validity_datetime = SplitDTField(label='DO Validity Date/Time')

    class Meta:
        model = TrailerPlacement
        fields = [
            'vendor', 'vehicle',
            'reporting_datetime', 'trip_start_datetime', 'exp_job_complete_datetime',
            'cut_off_datetime', 'do_validity_datetime',
            'trip_km', 'empty_running_kmr', 'veh_start_state', 'veh_start_city',
            'driver_mobile_no', 'driver_name', 'dl_no',
            'diesel_litres', 'diesel_rate', 'diesel_amount',
            'trailer_rent', 'other_expenses', 'trip_advance', 'trip_incentive',
            'customer_incentive', 'customer_job_no',
            'load_type', 'container_no_1', 'container_size_1',
            'container_no_2', 'container_size_2',
            'tracking_through', 'remarks',
        ]
        widgets = {
            'vendor': forms.Select(attrs=SEL),
            'vehicle': forms.Select(attrs=SEL),
            'trip_km': forms.NumberInput(attrs={**BS, 'step': '0.01'}),
            'empty_running_kmr': forms.NumberInput(attrs={**BS, 'step': '0.01'}),
            'veh_start_state': forms.TextInput(attrs=BS),
            'veh_start_city': forms.TextInput(attrs=BS),
            'driver_mobile_no': forms.TextInput(attrs={**BS, 'id': 'id_driver_mobile_no'}),
            'driver_name': forms.TextInput(attrs={**BS, 'id': 'id_driver_name'}),
            'dl_no': forms.TextInput(attrs={**BS, 'id': 'id_dl_no'}),
            'diesel_litres': forms.NumberInput(attrs={**BS, 'id': 'id_diesel_litres', 'step': '0.01'}),
            'diesel_rate': forms.NumberInput(attrs={**BS, 'id': 'id_diesel_rate', 'step': '0.01'}),
            'diesel_amount': forms.NumberInput(attrs={**BS, 'id': 'id_diesel_amount', 'readonly': True}),
            'trailer_rent': forms.NumberInput(attrs={**BS, 'step': '0.01'}),
            'other_expenses': forms.NumberInput(attrs={**BS, 'step': '0.01'}),
            'trip_advance': forms.NumberInput(attrs={**BS, 'step': '0.01'}),
            'trip_incentive': forms.NumberInput(attrs={**BS, 'step': '0.01'}),
            'customer_incentive': forms.NumberInput(attrs={**BS, 'step': '0.01'}),
            'customer_job_no': forms.TextInput(attrs=BS),
            'load_type': forms.Select(attrs=SEL),
            'container_no_1': forms.TextInput(attrs=BS),
            'container_size_1': forms.Select(
                choices=[('', '--'), ('20', '20'), ('40', '40'), ('45', '45')], attrs=SEL
            ),
            'container_no_2': forms.TextInput(attrs=BS),
            'container_size_2': forms.Select(
                choices=[('', '--'), ('20', '20'), ('40', '40'), ('45', '45')], attrs=SEL
            ),
            'tracking_through': forms.Select(attrs=SEL),
            'remarks': forms.Textarea(attrs=TA),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor'].queryset = Vendor.objects.filter(is_active=True)
        self.fields['vehicle'].queryset = Vehicle.objects.filter(is_active=True)
        optional = [
            'trip_km', 'empty_running_kmr', 'veh_start_state', 'veh_start_city',
            'driver_mobile_no', 'driver_name', 'dl_no',
            'diesel_litres', 'diesel_rate', 'diesel_amount',
            'trailer_rent', 'other_expenses', 'trip_advance', 'trip_incentive',
            'customer_incentive', 'customer_job_no', 'load_type',
            'container_no_1', 'container_size_1', 'container_no_2', 'container_size_2',
            'tracking_through', 'remarks',
        ]
        for f in optional:
            self.fields[f].required = False
