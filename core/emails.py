from urllib.parse import quote

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.utils.timezone import localtime


def registration_text(patient):
    return (
        f"Namaste {patient.name},\n\n"
        f"{settings.CLINIC_NAME} me aapka registration ho gaya hai. Aapke jaldi swasth hone ki kaamna hai.\n\n"
        f"Registration No : {patient.registration_no}\n"
        f"Naam            : {patient.name}\n"
        f"Age             : {patient.age}\n"
        f"Email           : {patient.email}\n"
        f"Physiotherapist : {patient.doctor}\n"
        f"Date & Time     : {localtime(patient.registered_at):%d-%m-%Y %I:%M %p}\n\n"
        f"Dhanyavaad,\n{settings.CLINIC_NAME}"
    )


def bill_text(payment):
    p = payment.patient
    lines = [
        f"Namaste {p.name},",
        "",
        f"{settings.CLINIC_NAME} ka payment details (physiotherapy):",
        "",
        f"Bill No  : {payment.bill_no}",
        f"Date     : {localtime(payment.created_at):%d-%m-%Y}",
        f"Patient  : {p.name} ({p.registration_no})",
        f"Physio    : {payment.treatment.doctor if payment.treatment else p.doctor}",
    ]
    if payment.treatment:
        t = payment.treatment
        end = t.end_date.strftime("%d-%m-%Y") if t.end_date else "Ongoing"
        lines.append(f"Treatment: {t.problem} ({t.start_date:%d-%m-%Y} se {end})")
        planned = f" / {t.sessions_planned}" if t.sessions_planned else ""
        lines.append(f"Sessions : {t.sessions_done}{planned}")
    if payment.description:
        lines.append(f"Details  : {payment.description}")
    lines += [
        f"Amount   : Rs. {payment.amount}",
        f"Status   : {payment.get_status_display()}",
        "",
        f"Dhanyavaad,\n{settings.CLINIC_NAME}",
    ]
    return "\n".join(lines)


def send_registration_email(patient):
    EmailMessage(
        subject=f"{settings.CLINIC_NAME} - Registration {patient.registration_no}",
        body=registration_text(patient),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[patient.email],
    ).send(fail_silently=False)


def send_bill_email(payment):
    EmailMessage(
        subject=f"{settings.CLINIC_NAME} - Payment {payment.bill_no} (Rs. {payment.amount})",
        body=bill_text(payment),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[payment.patient.email],
    ).send(fail_silently=False)
    payment.sent_at = timezone.now()
    payment.save(update_fields=["sent_at"])


def whatsapp_link(patient, text):
    number = patient.whatsapp_number
    if not number:
        return ""
    return f"https://wa.me/{number}?text={quote(text)}"
