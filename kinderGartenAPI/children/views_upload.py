from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

class UploadAvatarView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Save to /media/uploads/
        file_path = default_storage.save(f"uploads/{file_obj.name}", ContentFile(file_obj.read()))
        file_url = request.build_absolute_uri(f"/media/{file_path}")
        return Response({"url": file_url}, status=status.HTTP_201_CREATED)
