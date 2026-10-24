from datetime import date

from django.conf import settings
from django.db import models
from django.utils import timezone


class Doctor(models.Model):
    name = models.CharField(max_length=120)
    specialization = models.CharField(max_length=120, blank=True, help_text="Jaise: Sports / Ortho / Neuro Physiotherapist")
    phone = models.CharField(max_length=20, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"Dr. {self.name}" + (f" ({self.specialization})" if self.specialization else "")


class Patient(models.Model):
    GENDERS = [("M", "Male"), ("F", "Female"), ("O", "Other")]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField("Phone / WhatsApp", max_length=20, blank=True,
                             help_text="10 digit number ya country code ke sath (91XXXXXXXXXX)")
    age = models.PositiveSmallIntegerField()
    gender = models.CharField(max_length=1, choices=GENDERS, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="patients",
                               verbose_name="Consulting doctor / physiotherapist")
    registered_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-registered_at"]

    def __str__(self):
        return self.name

    @property
    def registration_no(self):
        return f"REG-{self.pk:05d}"

    @property
    def whatsapp_number(self):
        digits = "".join(c for c in self.phone if c.isdigit())
        if len(digits) == 10:
            digits = "91" + digits
        return digits


class Treatment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="treatments")
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT)
    THERAPIES = [
        ("exercise", "Exercise Therapy"),
        ("manual", "Manual Therapy / Mobilization"),
        ("electro", "Electrotherapy (TENS / IFT / Muscle Stim)"),
        ("ultrasound", "Ultrasound Therapy"),
        ("traction", "Traction"),
        ("dry_needling", "Dry Needling"),
        ("cupping", "Cupping"),
        ("hot_cold", "Hot / Cold Pack"),
        ("post_surgery", "Post-Surgery Rehab"),
        ("neuro", "Neuro Rehabilitation"),
        ("other", "Other"),
    ]
    problem = models.CharField("Complaint / Diagnosis", max_length=255,
                               help_text="Jaise: Lower back pain, Frozen shoulder, ACL rehab")
    body_part = models.CharField(max_length=100, blank=True, help_text="Jaise: Knee, Neck, Shoulder")
    therapy_type = models.CharField(max_length=20, choices=THERAPIES, blank=True)
    sessions_planned = models.PositiveSmallIntegerField("Planned sessions", null=True, blank=True)
    start_date = models.DateField("Treatment shuru (from)", default=date.today)
    end_date = models.DateField("Treatment khatam (to)", null=True, blank=True,
                                help_text="Abhi chal raha hai to khali chhod do")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.patient} - {self.problem}"

    @property
    def is_ongoing(self):
        return self.end_date is None

    @property
    def sessions_done(self):
        return len(self.visits.all())

    @property
    def total_days(self):
        end = self.end_date or date.today()
        return (end - self.start_date).days + 1


class Visit(models.Model):
    """Ek physiotherapy session (patient kis din aaya)."""
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name="visits")
    date = models.DateField("Session date", default=date.today)
    notes = models.CharField(max_length=255, blank=True, help_text="Jaise: Ultrasound + exercises, pain 4/10")

    class Meta:
        ordering = ["date"]
        verbose_name = "session"

    def __str__(self):
        return f"{self.treatment.patient} @ {self.date}"


class Payment(models.Model):
    STATUS = [("pending", "Pending"), ("paid", "Paid")]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="payments")
    treatment = models.ForeignKey(Treatment, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="payments")
    amount = models.DecimalField("Amount (₹)", max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True,
                                   help_text="Jaise: Session charges, exercise kit, consultation")
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    created_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.bill_no

    @property
    def bill_no(self):
        return f"BILL-{self.pk:05d}"
