from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Event, WeeklyPlan
from .serializers import EventSerializer, WeeklyPlanSerializer


# -------- Event ViewSet --------
class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Event.objects.all().order_by("date")
        class_id = self.request.query_params.get("class_name")
        if class_id:
            queryset = queryset.filter(class_name_id=class_id)
        return queryset


# -------- Weekly Plan ViewSet --------
class WeeklyPlanViewSet(viewsets.ModelViewSet):
    serializer_class = WeeklyPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = WeeklyPlan.objects.all().order_by("day", "time")
        class_id = self.request.query_params.get("class_name")
        if class_id:
            queryset = queryset.filter(class_name_id=class_id)
        return queryset

    def create(self, request, *args, **kwargs):
        print("📥 Incoming data:", request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("❌ Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.perform_create(serializer)
        except Exception as e:
            import traceback
            print("💥 Exception during save:")
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
