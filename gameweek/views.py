from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Game

def index(request):
    latest_game_list = Game.objects.order_by('-start_date')[:5]
    context = {'latest_game_list': latest_game_list}
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