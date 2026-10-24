import datetime

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Doctor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("specialization", models.CharField(blank=True, help_text="Jaise: Sports / Ortho / Neuro Physiotherapist", max_length=120)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Patient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, help_text="10 digit number ya country code ke sath (91XXXXXXXXXX)", max_length=20, verbose_name="Phone / WhatsApp")),
                ("age", models.PositiveSmallIntegerField()),
                ("gender", models.CharField(blank=True, choices=[("M", "Male"), ("F", "Female"), ("O", "Other")], max_length=1)),
                ("registered_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="patients", to="core.doctor", verbose_name="Consulting doctor / physiotherapist")),
            ],
            options={"ordering": ["-registered_at"]},
        ),
        migrations.CreateModel(
            name="Treatment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("problem", models.CharField(help_text="Jaise: Lower back pain, Frozen shoulder, ACL rehab", max_length=255, verbose_name="Complaint / Diagnosis")),
                ("body_part", models.CharField(blank=True, help_text="Jaise: Knee, Neck, Shoulder", max_length=100)),
                ("therapy_type", models.CharField(blank=True, choices=[("exercise", "Exercise Therapy"), ("manual", "Manual Therapy / Mobilization"), ("electro", "Electrotherapy (TENS / IFT / Muscle Stim)"), ("ultrasound", "Ultrasound Therapy"), ("traction", "Traction"), ("dry_needling", "Dry Needling"), ("cupping", "Cupping"), ("hot_cold", "Hot / Cold Pack"), ("post_surgery", "Post-Surgery Rehab"), ("neuro", "Neuro Rehabilitation"), ("other", "Other")], max_length=20)),
                ("sessions_planned", models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Planned sessions")),
                ("start_date", models.DateField(default=datetime.date.today, verbose_name="Treatment shuru (from)")),
                ("end_date", models.DateField(blank=True, help_text="Abhi chal raha hai to khali chhod do", null=True, verbose_name="Treatment khatam (to)")),
                ("notes", models.TextField(blank=True)),
                ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="core.doctor")),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="treatments", to="core.patient")),
            ],
            options={"ordering": ["-start_date"]},
        ),
        migrations.CreateModel(
            name="Visit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(default=datetime.date.today, verbose_name="Session date")),
                ("notes", models.CharField(blank=True, help_text="Jaise: Ultrasound + exercises, pain 4/10", max_length=255)),
                ("treatment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="visits", to="core.treatment")),
            ],
            options={"ordering": ["date"], "verbose_name": "session"},
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Amount (₹)")),
                ("description", models.CharField(blank=True, help_text="Jaise: Session charges, exercise kit, consultation", max_length=255)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("paid", "Paid")], default="pending", max_length=10)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="core.patient")),
                ("treatment", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="payments", to="core.treatment")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
