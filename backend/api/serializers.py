from rest_framework import serializers

from .models import Client, TourResult


class TourResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourResult
        fields = [
            "id",
            "client",
            "employee_name",
            "score",
            "total_score",
            "answered_questions",
            "total_questions",
            "items_found",
            "total_items",
            "completed_at",
        ]
        read_only_fields = ["id", "completed_at"]


class ClientSerializer(serializers.ModelSerializer):
    results_count = serializers.IntegerField(
        source="results.count", read_only=True
    )

    class Meta:
        model = Client
        fields = [
            "id",
            "name",
            "company",
            "logo_url",
            "primary_color",
            "tour_url",
            "created_at",
            "results_count",
        ]
        read_only_fields = ["id", "created_at", "results_count"]


class ReceiveResultSerializer(serializers.Serializer):
    """Payload accepted by the public POST /api/results/receive/ endpoint.

    The 3DVista tour sends a client identifier plus the score breakdown.
    `client` may be the Client id; alternatively `client_name` can be used
    to look the client up by name.
    """

    client = serializers.IntegerField(required=False)
    client_name = serializers.CharField(required=False)
    employee_name = serializers.CharField()
    score = serializers.IntegerField(default=0)
    total_score = serializers.IntegerField(default=0)
    answered_questions = serializers.IntegerField(default=0)
    total_questions = serializers.IntegerField(default=0)
    items_found = serializers.IntegerField(default=0)
    total_items = serializers.IntegerField(default=0)

    def validate(self, attrs):
        if not attrs.get("client") and not attrs.get("client_name"):
            raise serializers.ValidationError(
                "Provide either 'client' (id) or 'client_name'."
            )
        return attrs

    def create(self, validated_data):
        client_id = validated_data.pop("client", None)
        client_name = validated_data.pop("client_name", None)

        if client_id is not None:
            try:
                client = Client.objects.get(pk=client_id)
            except Client.DoesNotExist:
                raise serializers.ValidationError(
                    {"client": f"No client with id {client_id}."}
                )
        else:
            try:
                client = Client.objects.get(name__iexact=client_name)
            except Client.DoesNotExist:
                raise serializers.ValidationError(
                    {"client_name": f"No client named '{client_name}'."}
                )

        return TourResult.objects.create(client=client, **validated_data)
