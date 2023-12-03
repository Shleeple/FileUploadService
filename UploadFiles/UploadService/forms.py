from django import forms
from .models import Document
import re

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_file']
    
    def clean_document_file(self):
        document_file = self.cleaned_data.get('document_file')

        # check if the file is a docx file
        if not document_file.name.endswith('.docx'):
            raise forms.ValidationError('Invalid file type')

        return document_file