# reports/serializers.py
from rest_framework import serializers
from .models import DailyReport

class DailyReportSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source="child.name", read_only=True)

    class Meta:
        model = DailyReport
        fields = "__all__"

    def validate(self, attrs):
        tenant = self.context["request"].user.tenant
        child = attrs.get("child")
        date = attrs.get("date")

        if DailyReport.objects.filter(tenant=tenant, child=child, date=date).exists():
            raise serializers.ValidationError(
                f"Un rapport existe déjà pour {child.name} à la date {date}."
            )
        return attrs
