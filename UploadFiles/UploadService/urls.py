from django.urls import path
from .views import upload_document, download_document, user_login_view, home, document_list



urlpatterns = [
    path('', home, name='home'),
    path('login', user_login_view, name='login'),
    path('upload', upload_document, name='upload_document'),
    path('document_list', document_list, name='document_list'),
    path('download/<int:document_id>', download_document, name='download_document'),
]
