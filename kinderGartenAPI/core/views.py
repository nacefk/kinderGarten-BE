# core/views.py
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(["GET"])
def root_view(request):
    return Response({"message": "KinderGarten API Root"})
