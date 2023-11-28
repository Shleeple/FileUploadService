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
        
        """
        # check if the file name follows a specific naming convension using regex
        pattern = re.compile(r'(\w{1,4}ISD)|(\d+)[\s_]words|(FIE|ARD|IEP|Goals)')
        if not pattern.match(document_file.name):
            raise forms.ValidationError('Invalid file name. Follow the specified naming convention.')
        """

        return document_file