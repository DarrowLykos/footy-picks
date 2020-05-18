from django.urls import path, re_path, include

from . import views
from django.views.generic.base import RedirectView

app_name = 'picks_pages'

# TODO: change these to point to class based views instead
game_patterns = [
    # ex: /leagues/2/1
    path('', views.GameDetail.as_view(), name='game_detail'),
]

league_patterns = [
    # ex: /leagues/
    path('', views.LeagueList.as_view(), name='leagues_list'),
    # ex: /leagues/2/
    path('<int:league_id>/', views.LeagueDetail.as_view(),  name='league_detail'),
    # ex: /leagues/2/1
    path('<int:league_id>/<int:game_id>/', include(game_patterns)),
    # ex: leagues/create
    path('create/', views.CreateLeague.as_view(), name='create_league'),
    # ex: leagues/2/edit
    path('<int:league_id>/edit/', views.EditLeague.as_view(), name='edit_league'),
]

urlpatterns = league_patterns




"""

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
