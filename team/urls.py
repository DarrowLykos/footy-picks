from django.urls import path

from . import views

app_name = 'teams'
urlpatterns = [
    # ex: /teams/
    path('', views.index, name='index'),
    # ex: /teams/England
    path('<str:team_country>/', views.index, name='index'),
    # ex: /teams/England/Arsenal/
    path('<str:team_country>/<str:team_name>/', views.index, name='detail'),
    # ex: /teams/England/Premier_League
    path('<str:competition_country>/<str:competition_name>/', views.index, name='detail'),
    # ex: /teams/England/Premier_League/Matches
    path('<str:competition_country>/<str:match_competition>/Matches/', views.index, name='index'),
    # ex: /teams/England/Premier_League/Arsenal
    path('<str:competition_country>/<str:match_competition>/<str:team_name>/', views.index, name='detail'),
    # ex: /teams/England/Premier_League/Arsenal/Matches
    path('<str:competition_country>/<str:match_competition>/<str:team_name>/Matches/', views.index, name='index'),
    # ex: /teams/England/Premier_League/Arsenal/Matches/1
    path('<str:competition_country>/<str:match_competition>/<str:team_name>/Matches/<int:match_id>/', views.index, name='index'),


]