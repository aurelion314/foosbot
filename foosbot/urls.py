from django.urls import path
from . import views

urlpatterns = [
    path('', views.input),
    path('<int:client_id>/input_page', views.input),
    path('<int:client_id>/hash/<str:secret>', views.verify_hash),
    path('<int:client_id>/handler', views.handler),
    path('<int:client_id>/leaderboard', views.leaderboard),
    path('<int:client_id>/details', views.leaderboard_details),
]
