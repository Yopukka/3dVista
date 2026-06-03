from django.contrib import admin

from .models import Client, TourResult


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "company", "primary_color", "created_at")
    search_fields = ("name", "company")


@admin.register(TourResult)
class TourResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee_name",
        "client",
        "score",
        "total_score",
        "completed_at",
    )
    list_filter = ("client",)
    search_fields = ("employee_name",)
