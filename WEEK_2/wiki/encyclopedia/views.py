import os
import random

from django.shortcuts import render, redirect
from django.http import HttpResponse
from markdown2 import Markdown

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def view_entry(request, entry_name):
    markdown = Markdown()
    try:
        content = markdown.convert(util.get_entry(entry_name))
    except TypeError:
        return render(request, "encyclopedia/not_found.html")
    return render(request, "encyclopedia/entry.html", {
        "entry": content,
        "entry_name": entry_name
    })

def search_entries(request):
    search_query = request.GET.get('q', '').strip()
    entries = util.list_entries()
    if search_query in entries:
        return redirect('view_entry', entry_name=search_query)
    filtered_entries = [entry for entry in entries if search_query in entry]
    return render(request, 'encyclopedia/search_results.html', 
                    {'entries': filtered_entries, 'query': search_query})

def new_entry(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')

        entries = util.list_entries()

        if title in entries:
            return HttpResponse("Entry already exists.")
        util.save_entry(title, content)
        return redirect('view_entry', entry_name=title)

    return render(request, 'encyclopedia/new_entry.html')

def edit_entry(request, entry_title):
    if request.method == "POST":
        content = request.POST['content']
        util.save_entry(entry_title, content)
        return redirect('view_entry', entry_name=entry_title)
    content = util.get_entry(entry_title)
    if content is None:
        return HttpResponse("Entry does not exist.")
    return render(request, 'encyclopedia/edit_entry.html', {
        "entry_title": entry_title,
        "entry_content": content
    })

def random_entry(request):
    entries = util.list_entries()
    if entries:
        random_entry = random.choice(entries)
        entry_name = os.path.splitext(random_entry)[0]
        return redirect('view_entry', entry_name=entry_name)
    else:
        return redirect("index")