from django.urls import path, re_path, include, reverse

from . import views
from django.views.generic.base import RedirectView

app_name = 'picks_pages'

# TODO: add level before these for user specific views. e.g. footypicks.com/<user_id>/<league_id>/<game_id>
game_patterns = [
    # ex: /leagues/2/1
    path('', views.GameDetail.as_view(), name='game_detail'),
    # ex: leagues/2/5/predict
    path('predict/', views.PredictMatches.as_view(), name='predict_game'),
    path('performance/<int:player_id>/', views.ViewPredictions.as_view(), name='view_predictions'),
    # path('edit-predict/', views.EditPredictMatches.as_view(), name='predict_game_edit'),
    # path('predict/', views.ViewMatches.as_view(), name='predict_game'),
    # ex: leagues/2/5/prediction/1
    # path('predict/<int:', views.ViewPredictions.as_view(), name='predictions_detail'),
    # ex: leagues/2/5/edit
    ##path('edit/', views.EditGame.as_view(), name='edit_game'),
]

league_patterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('rules/', views.RulesView.as_view(), name='rules'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    # path('superadmin/', views.SuperAdminView.as_view(), name='superadmin'),
    path('profile/<int:pk>/', views.PlayerView.as_view(), name='player_profile'),
    # ex: /leagues/
    path('leagues/', views.LeagueList.as_view(), name='leagues_list'),
    # ex: /leagues/2/
    # path('<int:league_id>/', views.LeagueDetail.as_view(),  name='league_detail'),
    path('leagues/<int:league_id>/', views.GameList.as_view(), name='league_detail'),
    # path('<int:league_id>/', views.LeagueDetail.as_view(),  name='league_detail'),
    path('leagues/<int:league_id>/game/', views.GameList.as_view(), name='games_list'),
    # ex: /leagues/2/1
    path('leagues/<int:league_id>/game/<int:game_id>/', include(game_patterns)),
    # ex: leagues/2/games/create
    ##path('new-game/', views.CreateGame.as_view(), name='create_game'),
    # ex: leagues/create
    ##path('create/', views.CreateLeague.as_view(), name='create_league'),
    # ex: leagues/2/edit
    ##path('<int:league_id>/edit/', views.EditLeague.as_view(), name='edit_league'),
    # ex: leagues/2/join
    path('leagues/<int:league_id>/join/', views.JoinLeague.as_view(), name='join_league'),
    # ex: leagues/2/leave
    path('leagues/<int:league_id>/leave/', views.LeaveLeague.as_view(), name='leave_league'),
]

urlpatterns = league_patterns

