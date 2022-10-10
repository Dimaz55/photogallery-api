from django.core.files.uploadhandler import TemporaryFileUploadHandler

from app.exceptions import UploadSizeError
from config import settings


class SizeLimitUploadHandler(TemporaryFileUploadHandler):
    def __init__(self, request=None):
        super().__init__(request)

    def handle_raw_input(
            self, input_data, META, content_length, boundary, encoding=None):
        if content_length > settings.MAX_UPLOAD_SIZE:
            raise UploadSizeError
    