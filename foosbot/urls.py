from django.urls import path
from . import views

urlpatterns = [
    path('', views.input),
    path('<int:client_id>/input_page', views.input),
]
