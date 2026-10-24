from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),

    path("doctors/", views.doctor_list, name="doctor_list"),
    path("doctors/add/", views.doctor_form, name="doctor_add"),
    path("doctors/<int:pk>/edit/", views.doctor_form, name="doctor_edit"),

    path("patients/", views.patient_list, name="patient_list"),
    path("patients/add/", views.patient_add, name="patient_add"),
    path("patients/<int:pk>/", views.patient_detail, name="patient_detail"),
    path("patients/<int:pk>/edit/", views.patient_edit, name="patient_edit"),
    path("patients/<int:pk>/registration/", views.registration_form, name="registration_form"),
    path("patients/<int:pk>/send-registration/", views.send_registration, name="send_registration"),

    path("patients/<int:patient_pk>/treatment/add/", views.treatment_add, name="treatment_add"),
    path("treatments/<int:pk>/edit/", views.treatment_edit, name="treatment_edit"),
    path("treatments/<int:treatment_pk>/visit/add/", views.visit_add, name="visit_add"),

    path("patients/<int:patient_pk>/payment/add/", views.payment_add, name="payment_add"),
    path("payments/<int:pk>/", views.payment_detail, name="payment_detail"),
    path("payments/<int:pk>/send/", views.payment_send, name="payment_send"),
    path("payments/<int:pk>/paid/", views.payment_mark_paid, name="payment_mark_paid"),
]
