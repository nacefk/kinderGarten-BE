"""
Core validators for file uploads and data validation
"""

import mimetypes
from django.core.exceptions import ValidationError

ALLOWED_AVATAR_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "doc", "docx"}
ALLOWED_EXTENSIONS = ALLOWED_AVATAR_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS

MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_file_upload(file_obj, max_size=MAX_FILE_SIZE, allowed_types=None):
    """
    Validate uploaded file for size, extension, and MIME type.

    Args:
        file_obj: Django UploadedFile object
        max_size: Maximum file size in bytes
        allowed_types: Set of allowed MIME types

    Raises:
        ValidationError: If file doesn't pass validation
    """
    if allowed_types is None:
        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/gif",
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

    # Check size
    if file_obj.size > max_size:
        raise ValidationError(
            f"File too large. Maximum size is {max_size / 1024 / 1024}MB, "
            f"but got {file_obj.size / 1024 / 1024}MB"
        )

    # Check extension
    ext = file_obj.name.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"File type '.{ext}' not allowed. "
            f"Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file_obj.name)
    if mime_type not in allowed_types:
        raise ValidationError(
            f"File MIME type '{mime_type}' not allowed. "
            f"Allowed types: {', '.join(allowed_types)}"
        )

    return True
