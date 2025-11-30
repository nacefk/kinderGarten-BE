import logging
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, serializers

from core.validators import validate_file_upload, MAX_AVATAR_SIZE

logger = logging.getLogger("api")


class AvatarUploadSerializer(serializers.Serializer):
    """Serializer for avatar upload endpoint"""

    file = serializers.FileField()
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return None


class UploadAvatarView(APIView):
    """✅ SECURE: File upload with validation"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AvatarUploadSerializer  # For schema generation

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")

        if not file_obj:
            logger.warning(f"User {request.user.id} attempted upload with no file")
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Validate file
        try:
            validate_file_upload(
                file_obj,
                max_size=MAX_AVATAR_SIZE,
                allowed_types={"image/jpeg", "image/png", "image/gif"},
            )
        except ValidationError as e:
            logger.warning(f"File validation failed for user {request.user.id}: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # ✅ Generate safe filename (prevent directory traversal)
            ext = file_obj.name.split(".")[-1].lower()
            safe_name = f"{uuid.uuid4()}.{ext}"

            # ✅ Save to tenant-specific directory
            file_path = f"avatars/{request.user.tenant.slug}/{safe_name}"
            saved_path = default_storage.save(file_path, file_obj)
            file_url = request.build_absolute_uri(f"/media/{saved_path}")

            logger.info(f"Avatar uploaded by user {request.user.id}")

            return Response({"url": file_url}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error uploading file: {e}", exc_info=True)
            return Response(
                {"error": "File upload failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
