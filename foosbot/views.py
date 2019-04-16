from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def input(request, client_id):
    return render(request, 'foosbot/input.html')
    return HttpResponse('meow')