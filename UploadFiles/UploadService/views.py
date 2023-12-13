# import requirements
from .models import Document
from .forms import DocumentForm

from docx import Document as DocxDocument
import re
import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required


# // FIXME - Style the upload document page (change to see if changes worked)
# request to upload a document
@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # // TODO - Add clean_document_file from forms.py
            # Get the uploaded file
            uploaded_file = request.FILES['document_file']

            # Extract metadata using regex
            isd, word_count, document_type, document_name = extract_metadata(uploaded_file)
            # Generate a unique ID (you might want to make this more sophisticated)
            unique_id = f"{request.user.username}_{hash(document_name)}"

            now = timezone.localtime()
            current_time = now.strftime("%Y-%m-%d_%H:%M:%S")

            # Save to the database
            document = Document.objects.create(
                user=request.user,
                title=document_name,
                document_file=uploaded_file,
                isd=isd,
                word_count=word_count,
                document_type=document_type,
                upload_date=current_time,
                unique_id=unique_id,
            )

            return redirect('document_list')
    else:
        form = DocumentForm()

    return render(request, 'upload_document.html', {'form': form})


# // FIXME - Style upload document page, embed in document processing page
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


# // TODO - Add a view that shows progress in the processing of a document, then allows download
def process_document(document):
    # Load the original document using python-docx
    original_doc = Document(document.path)

    # Implement your processing logic here
    # For example, you might modify the document content

    return original_doc.unique_id


# // FIXME - Style document list page
@login_required
def document_list(request):
    documents = Document.objects.filter(user=request.user)  # Assuming you want to show only documents for the logged-in user
    return render(request, 'document_list.html', {'documents': documents})


# // FIXME - Fix regex to extract document metadata correctly
def extract_metadata(document_file):
    file_name = os.path.basename(document_file.name)
    print(f"File_name = {file_name}")
    # Use regex to extract metadata from the document title
    match = re.match(r'.*(\w{1,4}ISD).*(FIE|ARD|IEP).*(\d+)[\s_]*words', os.path.basename(document_file.name))
    
    if match:
        isd = match.group(1)  # Select the first group
        word_count = int(match.group(3))  # Select the third group
        document_type = match.group(2)  # Select the second group
        document_name = f"{document_type}_{isd}_{word_count}"
        return isd, word_count, document_type, document_name
    else:
        # Default values if regex doesn't match
        return 'Unknown', 0, 'Unknown', 'Unknown'


# // FIXME - Style login page
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


# // TODO - Create the landing page where the user can select whether to login or
def home(request):
    return render(request, 'home.html')
