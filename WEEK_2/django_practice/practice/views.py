from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def index(request):
     return render(request, "practice/index.html")

def matt(request):
     return HttpResponse("Hello, Matt!")

def greet(request, name):
     return render(request, "practice/greet.html", {
          "name": name.capitalize()
     })