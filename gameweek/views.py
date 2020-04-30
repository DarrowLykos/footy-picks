from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from datetime import datetime

from player.models import Player
from .models import Game, League
from player.models import Player

def index(request):
    current_player = request.user.player.id
    leagues_join_list = League.objects.filter(
        is_private=False, accepts_members=True).exclude(
        members__in=[current_player], owned_by=current_player).order_by('name')[:4]
    leagues_member_list = League.objects.filter(
        members__in=[current_player]).exclude(
        owned_by=current_player).order_by('name')[:4]
    leagues_owner_list = League.objects.filter(owned_by=current_player).order_by('name')[:4]
    context = {'leagues_join_list': leagues_join_list,
               'leagues_member_list': leagues_member_list,
               'leagues_owner_list': leagues_owner_list
               }
    return render(request, 'games/index.html', context)

def league_detail(request, league_id):
    current_player = request.user.player.id
    league = get_object_or_404(League, pk=league_id)
    is_owner = league.owned_by == current_player
    if is_owner or league.member_can_add:
        show_add_game = True
    else:
        show_add_game = False
    return render(request, 'games/league_detail.html', {'league': league, "show_add_game": show_add_game})

def games_index(request):
    now = datetime.now()
    latest_game_list = Game.objects.filter(start_date__gte=now).order_by('start_date')
    previous_game_list = Game.objects.filter(end_date__lte=now).order_by('start_date')
    live_game_list = Game.objects.filter(start_date__lte=now, end_date__gte=now).order_by('start_date')
    context = {'latest_game_list': latest_game_list, 
               'previous_game_list': previous_game_list,
               'live_game_list': live_game_list,
               'now': now
               }
    return render(request, 'games/games_index.html', context)

def results(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    return render(request, 'games/results.html', {'game': game})

def predict(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    return render(request, 'games/predict.html', {'game': game})