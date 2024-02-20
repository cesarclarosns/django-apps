from . import util
from django import forms
from django.forms.utils import ErrorList


def valid_title(title):
    for entry in util.list_entries():
        if title.lower() == entry.lower():
            return False
    return True


class DivErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ''
        return '<div class="errorlist">%s</div>' % ''.join(['<div class="alert alert-danger" role="alert">%s</div>' % e for e in self])


# Forms
class Create(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label="Content", widget=forms.Textarea(
        attrs={}))

    def clean_title(self):
        data = self.cleaned_data.get('title')
        if not valid_title(data):
            raise forms.ValidationError('The title already exists')
        return data


class Edit(forms.Form):
    content = forms.CharField(label="Content", widget=forms.Textarea(
        attrs={}))


class Search(forms.Form):
    q = forms.CharField(label="", widget=forms.TextInput(
        attrs={'class': 'form-control me-2', 
               'type': 'search', 
               'placeholder': 'Search',
               'aria-label': 'Search',
               'autocomplete': 'off'}))
