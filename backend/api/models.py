from django.db import models


class Client(models.Model):
    """A virtual-tour client (the company whose tour & stats we manage)."""

    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    logo_url = models.URLField(blank=True)
    primary_color = models.CharField(max_length=20, default="#2563eb")
    tour_url = models.URLField(
        blank=True,
        help_text="URL of the 3DVista virtual tour, loaded in an iframe.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TourResult(models.Model):
    """A single e-learning result submitted from a client's 3DVista tour."""

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="results",
    )
    employee_name = models.CharField(max_length=200)
    score = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    answered_questions = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    items_found = models.IntegerField(default=0)
    total_items = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.employee_name} — {self.score}/{self.total_score}"
