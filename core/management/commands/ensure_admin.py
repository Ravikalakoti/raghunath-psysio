import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "ADMIN_USERNAME / ADMIN_PASSWORD env se admin user banata hai (agar nahi hai)"

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME")
        password = os.environ.get("ADMIN_PASSWORD")
        email = os.environ.get("ADMIN_EMAIL", "")
        if not username or not password:
            self.stdout.write("ADMIN_USERNAME/ADMIN_PASSWORD set nahi hain, skip.")
            return
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write("Admin pehle se hai.")
            return
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Admin '{username}' ban gaya."))
