from django.urls import path
from . import views

urlpatterns = [
    path('', views.login),
    path('login', views.login),
    path('<int:account_id>/input', views.input),
    path('<int:account_id>/token', views.verify_token),
    path('<int:account_id>/handler', views.handler),
    path('leaderboard/<str:token>', views.leaderboard_token),
    path('<int:account_id>/leaderboard', views.leaderboard),
    path('<int:account_id>/details', views.leaderboard_details),
    path('<int:account_id>/setup', views.setup),
    path('<int:account_id>/player', views.player),
    path('<int:account_id>/remove_slack', views.remove_slack),
    path('slack', views.slack),
]
