# import requirements
from .models import Document
from .forms import DocumentForm

from docx import Document as DocxDocument
import re
import os

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
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

            # Extract metadata using regex
            isd, word_count, document_type, document_name = extract_metadata(uploaded_file)
            uploaded_file.name = document_name + ".docx"

            # Generate a unique ID (you might want to make this more sophisticated)
            unique_id = f"{request.user.username}_{hash(document_name)}"
            
            # set the time zone
            now = timezone.now()

            # Save to the database
            document = Document.objects.create(
                user=request.user,
                title=document_name,
                document_file=uploaded_file,
                isd=isd,
                word_count=word_count,
                document_type=document_type,
                upload_date=now,
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

    # set regex to extract each value
    isd_regex = r'(\w{1,4}ISD)'
    word_count_regex = r'(\d+)[\s_]words'
    document_type_regex = r'(FIE|ARD|IEP|Goals)'

    # Use regex to extract metadata from the document title
    isd_match = re.search(isd_regex, os.path.basename(document_file.name))
    word_count_match = re.search(word_count_regex, os.path.basename(document_file.name))
    document_type_match = re.search(document_type_regex, os.path.basename(document_file.name))
    
    # Set values if exist, otherwise set to None
    if isd_match:
        isd = isd_match.group(1)
    else:
        isd = "Unknown"

    if word_count_match:
        word_count = word_count_match.group(1)
    else:
        word_count = 0

    if document_type_match:
        document_type = document_type_match.group(1)
    else:
        document_type = "Unknown"

    document_name = f"{document_type}_{isd}_{word_count}"
    return isd, word_count, document_type, document_name


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
