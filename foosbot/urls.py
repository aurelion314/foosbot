from django.urls import path
from . import views

urlpatterns = [
    path('', views.input),
    path('<int:client_id>/input_page', views.input),
    path('<int:client_id>/hash/<str:secret>', views.verify_hash),
    path('<int:client_id>/handler', views.handler),
]
