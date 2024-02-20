from . import forms
from . import util
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
import markdown2
import random


# Create new encyclopedia entry
def create(request):
    if request.method == "POST":
        form = forms.Create(request.POST, error_class=forms.DivErrorList)
        if form.is_valid():
            content = form.cleaned_data['content']
            title = form.cleaned_data['title']
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("encyclopedia:render_entry", kwargs={'q': title}))
        else:
            return render(request, "encyclopedia/create.html", {
                'create': form,
                'search': forms.Search()
            })
    else:
        return render(request, "encyclopedia/create.html", {
            'create': forms.Create(),
            'search': forms.Search()
        })


# Edit an existing encyclopedia entry
def edit(request, q):
    # Submitting form to update an entry (edit the entry)
    if request.method == "POST":
        form = forms.Edit(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            util.save_entry(q, content)
            return HttpResponseRedirect(reverse("encyclopedia:render_entry", kwargs={'q': q}))
        else:
            return render(request, "encyclopedia/edit.html", {
                'content': form,
                'search': forms.Search(),
                'title': q
            })
    # Loading the form to edit the entry
    else:
        return render(request, "encyclopedia/edit.html", {
            'content': forms.Edit(initial={'content': util.get_entry(q)}),
            'search': forms.Search(),
            'title': q
        })


# Index page / Search results
def index(request):
    # Search results
    if request.method == "POST":
        form = forms.Search(request.POST)
        if form.is_valid():
            q = form.cleaned_data["q"].lower()
            for entry in util.list_entries():
                if q == entry.lower():
                    return HttpResponseRedirect(reverse("encyclopedia:render_entry", kwargs={'q': entry}))
            return render(request, "encyclopedia/search.html", {
                'entries': list(entry for entry in util.list_entries() if q in entry.lower()),
                'search': forms.Search()
            })
        else:
            return HttpResponseRedirect(reverse("encyclopedia:index"))
    # Index page
    else:
        return render(request, "encyclopedia/index.html", {
            'entries': util.list_entries(),
            'search': forms.Search()
        })


# Random encyclopedia entry
def random_entry(request):
    entry = random.choice(util.list_entries())
    return HttpResponseRedirect(reverse("encyclopedia:render_entry", kwargs={'q': entry}))


# Encyclopedia entry page
def render_entry(request, q):
    for entry in util.list_entries():
        if entry.lower() == q.lower():
            return render(request, "encyclopedia/entry.html", {
                'entry': markdown2.markdown(util.get_entry(entry)),
                'search': forms.Search(),
                'title': entry
            })
    return render(request, "encyclopedia/notfound.html", {
        'search': forms.Search(),
        'title': q
    })
