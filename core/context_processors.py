from django.conf import settings

def clinic(request):
    return {
        "CLINIC_NAME": settings.CLINIC_NAME,
        "CLINIC_TAGLINE": settings.CLINIC_TAGLINE,
        "CLINIC_PHONE": settings.CLINIC_PHONE,
        "CLINIC_ADDRESS": settings.CLINIC_ADDRESS,
    }
