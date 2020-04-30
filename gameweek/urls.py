from django.urls import path

from . import views

app_name = 'leagues'
urlpatterns = [
    # ex: /leagues/
    path('', views.index, name='leagues_list'),
    # ex: /leagues/2/
    path('<int:league_id>/', views.league_detail,  name='league_detail'),
    # ex: /leagues/2/games
    path('<int:league_id>/games', views.games_index, name='games_index'),

]

"""
# ex: leagues/create
path('create/', views.index, name='create'),
# ex: leagues/2/edit
path('<int:league_id>/edit/', views.index, name='create'),
# ex: leagues/2/join
path('<int:league_id>/join/', views.index, name='join'),
# ex: leagues/2/leave
path('<int:league_id>/leave/', views.index, name='leave'),
# ex: leagues/2/players
path('<int:league_id>/players/', views.index, name='players'),
# ex: leagues/2/games/5/
path('<int:league_id>/games/<int:game_id>/', views.detail, name='detail'),
# ex: leagues/2/games/5/results
path('<int:league_id>/games/<int:game_id>/results/', views.results, name='results'),
# ex: leagues/2/games/5/predict
path('<int:league_id>/games/<int:game_id>/predict/', views.predict, name='predict'),
# ex: leagues/2/games/create
path('<int:league_id>/games/create/', views.index, name='create'),
# ex: leagues/2/games/5/edit
path('<int:league_id>/games/<int:game_id>/edit/', views.index, name='create'),
# ex: leagues/2/games/5/join
path('<int:league_id>/games/<int:game_id>/join/', views.index, name='join'),
# ex: leagues/2/games/5/leave
path('<int:league_id>/games/<int:game_id>/leave/', views.index, name='leave'),
# ex: leagues/2/games/5/players
path('<int:league_id>/games/<int:game_id>/players/', views.index, name='players'),
"""
