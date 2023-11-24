from .models import Document
from .forms import DocumentForm

from docx import Document as DocxDocument
import re
import os
import requests

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
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

            return render(request, 'upload_document.html', {'document': document})
    else:
        form = DocumentForm()

    return render(request, 'upload_document.html', {'form': form})


@login_required
def download_document(request, document_id):
    document = Document.objects.get(id=document_id)

    # Perform processing on the document (you'll need to implement this)
    processed_file_path = process_document(document)

    # Use Django's FileResponse to serve the processed file for download
    with open(processed_file_path, 'rb') as processed_file:
        response = HttpResponse(processed_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename={document.title}_processed.docx'
    
    # Delete the processed file after serving
    os.remove(processed_file_path)

    return response


def extract_metadata(document_file):
    # Use regex to extract metadata from the document title
    match = re.match(r'(?P<isd>[A-Z0-9]+)_(?P<word_count>\d+)_(?P<document_type>[A-Za-z]+)', document_file.name)
    
    if match:
        isd = match.group('isd')
        word_count = int(match.group('word_count'))
        document_type = match.group('document_type')
        return isd, word_count, document_type
    else:
        # Default values if regex doesn't match
        return 'Unknown', 0, 'Unknown'


def process_document(document):
    # Implement your processing logic here
    # For example, you might use the python-docx library to modify the document
    # Save the processed document to a new file
    processed_file_path = os.path.join(settings.MEDIA_ROOT, 'processed', f"{document.title}_processed.docx")

    # This is a placeholder, you'll need to implement the actual processing
    # Here, we're just copying the original file to the processed file path
    with open(document.document_file.path, 'rb') as original_file:
        with open(processed_file_path, 'wb') as processed_file:
            processed_file.write(original_file.read())

    return processed_file_path


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


def document_list(request):
    documents = Document.objects.filter(user=request.user)  # Assuming you want to show only documents for the logged-in user
    return render(request, 'document_list.html', {'documents': documents})