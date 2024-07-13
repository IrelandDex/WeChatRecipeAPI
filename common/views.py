from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .cos_utils import upload_file
import os


class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        file = request.FILES.get('file')
        file_key = request.data.get('key')

        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        if not file_key:
            return Response({'error': 'No file key provided'}, status=status.HTTP_400_BAD_REQUEST)

        file_name = file.name
        file_key = file_key or f'uploads/{file_name}'

        etag = upload_file(file, file_key)
        if etag:
            file_url = f'https://{os.environ.get("BUCKET_NAME")}.cos.ap-shanghai.myqcloud.com/{file_key}'
            return Response({'file_url': file_url}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'File upload failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
