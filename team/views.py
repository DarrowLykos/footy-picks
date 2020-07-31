from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, get_list_or_404
from datetime import datetime
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView, View
from .models import Match


# Create your views here.
def detail(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    return render(request, 'games/_detail.html', {'game': game})


class FixturesList(ListView):
    model = Match
    template_name = "team/partials/fixtures_list.html"
