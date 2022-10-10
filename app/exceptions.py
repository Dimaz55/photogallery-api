from rest_framework import status
from rest_framework.exceptions import APIException


class UploadSizeError(APIException):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    default_detail = 'File size exceeds maximum allowed'
