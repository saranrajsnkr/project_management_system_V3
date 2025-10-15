from django import forms

class CsvImportForm(forms.Form):
    csv_upload = forms.FileField(label="Select CSV file")
