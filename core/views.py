from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import emails
from .forms import DoctorForm, PatientForm, PaymentForm, TreatmentForm, VisitForm
from .models import Doctor, Patient, Payment, Treatment


def _form_page(request, form, title, back="dashboard"):
    return render(request, "form.html", {"form": form, "title": title, "back": back})


@login_required
def dashboard(request):
    ctx = {
        "patient_count": Patient.objects.count(),
        "doctor_count": Doctor.objects.filter(active=True).count(),
        "ongoing": Treatment.objects.filter(end_date__isnull=True).count(),
        "pending_amount": Payment.objects.filter(status="pending").aggregate(s=Sum("amount"))["s"] or 0,
        "recent": Patient.objects.select_related("doctor")[:8],
    }
    return render(request, "dashboard.html", ctx)


# ---------- Doctors ----------
@login_required
def doctor_list(request):
    return render(request, "doctor_list.html", {"doctors": Doctor.objects.all()})


@login_required
def doctor_form(request, pk=None):
    doctor = get_object_or_404(Doctor, pk=pk) if pk else None
    form = DoctorForm(request.POST or None, instance=doctor)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Doctor saved successfully.")
        return redirect("doctor_list")
    return _form_page(request, form, "Edit Doctor" if doctor else "New Doctor", "doctor_list")


# ---------- Patients ----------
@login_required
def patient_list(request):
    q = request.GET.get("q", "").strip()
    patients = Patient.objects.select_related("doctor")
    if q:
        patients = patients.filter(Q(name__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q))
    return render(request, "patient_list.html", {"patients": patients, "q": q})


@login_required
def patient_add(request):
    form = PatientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        patient = form.save(commit=False)
        patient.created_by = request.user
        patient.save()
        messages.success(request, f"Patient registered: {patient.registration_no}")
        if form.cleaned_data.get("send_email"):
            try:
                emails.send_registration_email(patient)
                messages.success(request, f"Registration email has been sent to {patient.email}.")
            except Exception as exc:
                messages.error(request, f"Email failed to send: {exc}")
        return redirect("patient_detail", pk=patient.pk)
    return _form_page(request, form, "New Patient Registration", "patient_list")


@login_required
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientForm(request.POST or None, instance=patient)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Patient updated successfully.")
        return redirect("patient_detail", pk=pk)
    return _form_page(request, form, f"Edit: {patient.name}", "patient_list")


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient.objects.select_related("doctor"), pk=pk)
    return render(request, "patient_detail.html", {
        "patient": patient,
        "treatments": patient.treatments.select_related("doctor").prefetch_related("visits"),
        "payments": patient.payments.all(),
        "wa_link": emails.whatsapp_link(patient, emails.registration_text(patient)),
    })


@login_required
def registration_form(request, pk):
    patient = get_object_or_404(Patient.objects.select_related("doctor"), pk=pk)
    return render(request, "registration_form.html", {
        "patient": patient,
        "wa_link": emails.whatsapp_link(patient, emails.registration_text(patient)),
    })


@login_required
@require_POST
def send_registration(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    try:
        emails.send_registration_email(patient)
        messages.success(request, f"Registration email has been sent to {patient.email}.")
    except Exception as exc:
        messages.error(request, f"Email failed to send: {exc}")
    return redirect("patient_detail", pk=pk)


# ---------- Treatment / Visits ----------
@login_required
def treatment_add(request, patient_pk):
    patient = get_object_or_404(Patient, pk=patient_pk)
    form = TreatmentForm(request.POST or None, initial={"doctor": patient.doctor})
    if request.method == "POST" and form.is_valid():
        t = form.save(commit=False)
        t.patient = patient
        t.save()
        messages.success(request, "Treatment added successfully.")
        return redirect("patient_detail", pk=patient.pk)
    return _form_page(request, form, f"Add Treatment: {patient.name}", "patient_list")


@login_required
def treatment_edit(request, pk):
    t = get_object_or_404(Treatment, pk=pk)
    form = TreatmentForm(request.POST or None, instance=t)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Treatment updated successfully.")
        return redirect("patient_detail", pk=t.patient_id)
    return _form_page(request, form, "Edit Treatment", "patient_list")


@login_required
def visit_add(request, treatment_pk):
    t = get_object_or_404(Treatment, pk=treatment_pk)
    form = VisitForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        v = form.save(commit=False)
        v.treatment = t
        v.save()
        messages.success(request, "Session added successfully.")
        return redirect("patient_detail", pk=t.patient_id)
    return _form_page(request, form, f"Add Session: {t.patient.name} - {t.problem}", "patient_list")


# ---------- Payments ----------
@login_required
def payment_add(request, patient_pk):
    patient = get_object_or_404(Patient, pk=patient_pk)
    form = PaymentForm(patient, request.POST or None)
    if request.method == "POST" and form.is_valid():
        p = form.save(commit=False)
        p.patient = patient
        p.save()
        messages.success(request, f"Payment invoice {p.bill_no} generated successfully.")
        return redirect("payment_detail", pk=p.pk)
    return _form_page(request, form, f"Generate Payment: {patient.name}", "patient_list")


@login_required
def payment_detail(request, pk):
    payment = get_object_or_404(Payment.objects.select_related("patient", "treatment"), pk=pk)
    return render(request, "bill_detail.html", {
        "p": payment,
        "wa_link": emails.whatsapp_link(payment.patient, emails.bill_text(payment)),
    })


@login_required
@require_POST
def payment_send(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    try:
        emails.send_bill_email(payment)
        messages.success(request, f"Payment details have been sent to {payment.patient.email}.")
    except Exception as exc:
        messages.error(request, f"Email failed to send: {exc}")
    return redirect("payment_detail", pk=pk)


@login_required
@require_POST
def payment_mark_paid(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    payment.status = "paid"
    payment.save(update_fields=["status"])
    messages.success(request, "Payment has been marked as 'Paid'.")
    return redirect("payment_detail", pk=pk)
