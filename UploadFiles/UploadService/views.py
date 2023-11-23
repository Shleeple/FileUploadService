from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Document
from .forms import DocumentForm
import re
from docx import Document as DocxDocument
import os
from django.conf import settings
import requests
from django.contrib.auth.decorators import login_required

# request to upload a document
@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            title = form.cleaned_data['title']
            document_file = form.cleaned_data['document_file']

            # Extract metadata using regex and docx library
            isd, word_count, document_type = extract_metadata(document_file)

            # Generate a unique ID (you might want to make this more sophisticated)
            unique_id = f"{user.username}_{title}_{hash(document_file.name)}"

            # Save to the database
            Document.objects.create(
                user=user,
                title=title,
                document_file=document_file,
                isd=isd,
                word_count=word_count,
                document_type=document_type,
                unique_id=unique_id,
            )

            return redirect('document_list')  # Redirect to a page showing a list of uploaded documents
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
