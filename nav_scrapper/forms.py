from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(label="Search Query", max_length=255)
