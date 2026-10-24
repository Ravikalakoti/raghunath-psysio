# Raghunath Physiotherapy - Patient Manager (Django + Brevo + Render)

Admin login -> Physiotherapists add -> Patient registration (name, email, age, timestamp, physio) ->
Treatment (condition, therapy type, from-to dates, session dates) -> Payment generate -> Email (Brevo) / WhatsApp.

## Local run
    python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    DEBUG=True python manage.py runserver
(Bina BREVO_API_KEY ke email terminal me print hoti hai.)

## Render deploy
1. Code GitHub pe push karo.
2. Render -> New -> Blueprint -> repo select (render.yaml auto detect hoga).
3. Environment variables bharo: BREVO_API_KEY, DEFAULT_FROM_EMAIL, ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL, CLINIC_NAME, CLINIC_PHONE, CLINIC_ADDRESS (bill/form ke letterhead me dikhte hain).
4. Deploy. Build ke time admin user khud ban jaata hai.

## Brevo setup
- Brevo -> SMTP & API -> API Keys -> v3 key banao (SMTP key nahi).
- Senders -> apna sender email verify karo; wahi DEFAULT_FROM_EMAIL me use karo, jaise:  Raghunath Physiotherapy <you@gmail.com>
