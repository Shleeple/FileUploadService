from django.urls import path
from .views import upload_document, download_document

urlpatterns = [
    path('upload/', upload_document, name='upload_document'),
    path('download/<int:document_id>/', download_document, name='download_document'),
]
