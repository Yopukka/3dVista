"""Idempotent production bootstrap, safe to run on every deploy.

Creates the admin superuser from DJANGO_SUPERUSER_* env vars if it doesn't
exist, and (optionally) seeds the demo Acme client + sample results when the
database is empty and DEMO_TOUR_URL is set.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Ensure the admin superuser exists; optionally seed a demo client."

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")

        if not User.objects.filter(username=username).exists():
            if not password:
                self.stdout.write(
                    self.style.WARNING(
                        "DJANGO_SUPERUSER_PASSWORD not set — skipping superuser creation."
                    )
                )
            else:
                User.objects.create_superuser(username, email, password)
                self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))
        else:
            self.stdout.write(f"Superuser '{username}' already exists.")

        # Optional demo seed (only when DB is empty and a tour URL is provided).
        from api.models import Client, TourResult

        tour_url = os.environ.get("DEMO_TOUR_URL")
        if tour_url and not Client.objects.exists():
            c = Client.objects.create(
                name="Acme Safety Tour",
                company="Acme Corp",
                logo_url="https://dummyimage.com/200x80/2563eb/ffffff&text=ACME",
                primary_color="#2563eb",
                tour_url=tour_url,
            )
            TourResult.objects.create(
                client=c, employee_name="Jane Doe", score=8, total_score=10,
                answered_questions=10, total_questions=10, items_found=4, total_items=5,
            )
            TourResult.objects.create(
                client=c, employee_name="John Smith", score=6, total_score=10,
                answered_questions=9, total_questions=10, items_found=3, total_items=5,
            )
            self.stdout.write(self.style.SUCCESS("Seeded demo Acme client + results."))
