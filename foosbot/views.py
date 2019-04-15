from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def input(request, client_id):
    return render('input')
    return HttpResponse('meow')