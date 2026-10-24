from datetime import date

from django import forms

from .models import Doctor, Patient, Treatment, Visit, Payment


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["name", "specialization", "phone", "active"]


class PatientForm(forms.ModelForm):
    send_email = forms.BooleanField(required=False, initial=True,
                                    label="Send email after save")

    class Meta:
        model = Patient
        fields = ["name", "email", "phone", "age", "gender", "doctor"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doctor"].queryset = Doctor.objects.filter(active=True)
        if self.instance.pk:
            del self.fields["send_email"]


class TreatmentForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}),
                                 initial=date.today, label="Treatment start (from)")
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), required=False,
                               label="Treatment end (to)",
                               help_text="Leave blank if treatment is active")

    class Meta:
        model = Treatment
        fields = ["doctor", "problem", "body_part", "therapy_type", "sessions_planned", "start_date", "end_date", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doctor"].queryset = Doctor.objects.filter(active=True)

    def clean(self):
        data = super().clean()
        s, e = data.get("start_date"), data.get("end_date")
        if s and e and e < s:
            self.add_error("end_date", "End date cannot be earlier than the start date.")
        return data


class VisitForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), initial=date.today)

    class Meta:
        model = Visit
        fields = ["date", "notes"]


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["treatment", "amount", "description", "status"]

    def __init__(self, patient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["treatment"].queryset = patient.treatments.all()
        self.fields["treatment"].required = False
