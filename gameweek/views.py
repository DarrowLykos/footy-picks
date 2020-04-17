from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from datetime import datetime

from .models import Game

def index(request):
    now = datetime.now()
    latest_game_list = Game.objects.filter(start_date__gte=now).order_by('start_date')
    previous_game_list = Game.objects.filter(end_date__lte=now).order_by('start_date')
    live_game_list = Game.objects.filter(start_date__lte=now, end_date__gte=now).order_by('start_date')
    context = {'latest_game_list': latest_game_list, 
               'previous_game_list': previous_game_list,
               'live_game_list': live_game_list,
               'now' : now
               }
    return render(request, 'games/index.html', context)

def detail(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    return render(request, 'games/detail.html', {'game': game})

def results(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    return render(request, 'games/results.html', {'game': game})

def predict(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    return render(request, 'games/predict.html', {'game': game})