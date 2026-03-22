from django import forms
from django.utils import timezone

from .models import LegStatusUpdate, ProofOfDelivery

BS = {'class': 'form-control form-control-sm'}
SEL = {'class': 'form-select form-select-sm'}
TA = {'class': 'form-control form-control-sm', 'rows': 2}


class LegStatusUpdateForm(forms.ModelForm):
    status_datetime = forms.SplitDateTimeField(
        required=True,
        initial=timezone.now,
        widget=forms.SplitDateTimeWidget(
            date_attrs={'type': 'date', **BS},
            time_attrs={'type': 'time', **BS},
        ),
    )

    class Meta:
        model = LegStatusUpdate
        fields = ['status', 'status_datetime', 'remarks', 'gps_location', 'is_other_info']
        widgets = {
            'status': forms.Select(attrs=SEL),
            'remarks': forms.Textarea(attrs=TA),
            'gps_location': forms.TextInput(attrs={**BS, 'placeholder': 'GPS Location'}),
            'is_other_info': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill datetime with current time
        if not self.initial.get('status_datetime') and not self.data.get('status_datetime_0'):
            now = timezone.localtime(timezone.now())
            self.initial['status_datetime'] = now
        self.fields['remarks'].required = False
        self.fields['gps_location'].required = False
        self.fields['is_other_info'].required = False


class PODUploadForm(forms.ModelForm):
    class Meta:
        model = ProofOfDelivery
        fields = ['pod_type', 'file', 'delivery_date', 'remarks']
        widgets = {
            'pod_type': forms.Select(attrs=SEL),
            'file': forms.ClearableFileInput(attrs={**BS, 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'delivery_date': forms.DateInput(attrs={'type': 'date', **BS}),
            'remarks': forms.Textarea(attrs=TA),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delivery_date'].required = False
        self.fields['remarks'].required = False
