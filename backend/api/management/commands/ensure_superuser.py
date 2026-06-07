"""Idempotent production bootstrap, safe to run on every deploy.

On each deploy this command:
  - creates the admin superuser from DJANGO_SUPERUSER_* env vars, or syncs its
    password to DJANGO_SUPERUSER_PASSWORD if the user already exists (so the env
    var is the single source of truth for the login — no lockouts), and
  - ensures the demo Acme client exists and points to DEMO_TOUR_URL (creating it
    with sample results, or updating the tour_url if it changed).
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Ensure the admin superuser + demo Acme client are in sync with env."

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")

        user = User.objects.filter(username=username).first()
        if user is None:
            if password:
                User.objects.create_superuser(username, email, password)
                self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "DJANGO_SUPERUSER_PASSWORD not set — skipping superuser creation."
                    )
                )
        elif password:
            # Keep the login password in sync with the env var (prevents lockouts).
            user.set_password(password)
            user.is_staff = user.is_superuser = user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Synced password for '{username}'."))

        # Ensure the demo Acme client exists and points to the current tour URL.
        from api.models import Client, TourResult

        tour_url = os.environ.get("DEMO_TOUR_URL")
        if tour_url:
            client, created = Client.objects.get_or_create(
                name="Acme Safety Tour",
                defaults={
                    "company": "Acme Corp",
                    "logo_url": "https://dummyimage.com/200x80/2563eb/ffffff&text=ACME",
                    "primary_color": "#2563eb",
                    "tour_url": tour_url,
                },
            )
            if client.tour_url != tour_url:
                client.tour_url = tour_url
                client.save(update_fields=["tour_url"])
            if created:
                TourResult.objects.create(
                    client=client, employee_name="Jane Doe", score=8, total_score=10,
                    answered_questions=10, total_questions=10, items_found=4, total_items=5,
                )
                TourResult.objects.create(
                    client=client, employee_name="John Smith", score=6, total_score=10,
                    answered_questions=9, total_questions=10, items_found=3, total_items=5,
                )
            verb = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{verb} Acme client -> {tour_url}"))
