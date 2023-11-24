# import requirements
from .models import Document
from .forms import DocumentForm

from docx import Document as DocxDocument
import re
import os
import io
import requests

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

# request to upload a document
@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the uploaded file
            uploaded_file = request.FILES['document_file']

            # Truncate the original filename to fit within the allowed length
            max_length = 100  # Adjust this based on your requirements
            original_filename = uploaded_file.name[:max_length]

            # Extract metadata using regex and docx library
            isd, word_count, document_type = extract_metadata(uploaded_file)

            # Generate a unique ID (you might want to make this more sophisticated)
            unique_id = f"{request.user.username}_{original_filename}_{hash(uploaded_file.name)}"

            # Save to the database
            document = Document.objects.create(
                user=request.user,
                title=original_filename,
                document_file=uploaded_file,
                isd=isd,
                word_count=word_count,
                document_type=document_type,
                unique_id=unique_id,
            )

            return redirect('document_list')
    else:
        form = DocumentForm()

    return render(request, 'upload_document.html', {'form': form})


@login_required
def download_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if document.processed_document:
        # Download the processed document
        processed_document = document.processed_document.processed_document_file
        response = HttpResponse(processed_document.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(processed_document.name)}"'
    else:
        # Download the original document
        original_document = document.document_file
        response = HttpResponse(original_document.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(original_document.name)}"'

    return response


@login_required
def document_list(request):
    documents = Document.objects.filter(user=request.user)  # Assuming you want to show only documents for the logged-in user
    return render(request, 'document_list.html', {'documents': documents})


def extract_metadata(document_file):
    file_name = os.path.basename(document_file.name)
    print(f"File_name = {file_name}")
    # Use regex to extract metadata from the document title
    match = re.match(r'.*(\w{2,3}ISD).*(FIE|ARD|IEP).*\s+(\d+) words', os.path.basename(document_file.name))
    
    if match:
        isd = match.group(1)  # Select the first group
        word_count = int(match.group(3))  # Select the third group
        document_type = match.group(2)  # Select the second group
        return isd, word_count, document_type
    else:
        # Default values if regex doesn't match
        return 'Unknown', 0, 'Unknown'


def process_document(document):
    # Load the original document using python-docx
    original_doc = Document(document.path)

    # Implement your processing logic here
    # For example, you might modify the document content

    return original_doc.unique_id


def user_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('upload_document')  # Redirect to the upload document page after login
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def home(request):
    return render(request, 'home.html')
