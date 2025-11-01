from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from .models import User

def home(request):
    #return render(request,"findeur/home.html")
    return HttpResponse("test")