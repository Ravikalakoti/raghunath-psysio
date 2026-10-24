from django.contrib import admin
from .models import Doctor, Patient, Treatment, Visit, Payment

for m in (Doctor, Patient, Treatment, Visit, Payment):
    admin.site.register(m)
