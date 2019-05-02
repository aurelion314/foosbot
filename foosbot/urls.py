from django.urls import path
from . import views

urlpatterns = [
    path('', views.input),
    path('<int:account_id>/input', views.input),
    path('<int:account_id>/hash/<str:token>', views.verify_hash),
    path('<int:account_id>/handler', views.handler),
    path('<int:account_id>/leaderboard', views.leaderboard),
    path('<int:account_id>/details', views.leaderboard_details),
]
