from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from datetime import datetime
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from player.models import Player
from .models import Game, League, Prediction
from player.models import Player

# TODO: change all of these to generic class based views
# TODO: split leagues HTML and views DRY

class LeagueList(ListView):
    model = League
    template_name = 'games/index.html'

    # TODO: do the thing that makes this viewable by logged in users only
    def get_context_data(self, **kwargs):
        try:
            current_player = self.user.player.id
        except AttributeError:
            current_player = None
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['leagues_join_list'] = League.objects.filter(
        is_private=False, accepts_members=True).exclude(
        members__in=[current_player], owned_by=current_player).order_by('name')[:4]
        context['leagues_member_list'] = League.objects.filter(
        members__in=[current_player]).exclude(
        owned_by=current_player).order_by('name')[:4]
        context['leagues_owner_list'] = League.objects.filter(
            members__in=[current_player]).exclude(
            owned_by=current_player).order_by('name')[:4]
        return context

class LeagueDetail(DetailView):
    model = League
    template_name = 'games/league_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs.get("league_id"))

    def get_context_data(self, **kwargs):
        try:
            current_player = self.user.player.id
        except AttributeError:
            current_player = None
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        is_owner = self.object.owned_by.id == current_player
        is_member = self.object.is_member(current_player)
        # if league.member_can_add and league.objects.filter(members__in=[Player.current_player]):
        if self.object.member_can_add and is_member:
            member_can_add = True
        else:
            member_can_add = False
        if is_owner or member_can_add:
            show_add_game = True
        else:
            show_add_game = False
        context['show_add_game'] = show_add_game
        context['is_member'] = is_member
        return context

class GameDetail(DetailView):
    model = Game
    template_name = 'games/game_detail.html'

    def get_object(self, queryset=None):
        queryset = self.model.objects.filter(included_in_league=self.kwargs.get("league_id"))
        return get_object_or_404(queryset, pk=self.kwargs.get("game_id"))

    def get_context_data(self, **kwargs):
        try:
            current_player = self.user.player.id
        except AttributeError:
            current_player = None
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        players = self.object.get_players(self.kwargs.get("league_id"))
        leaderboard = Prediction.objects.get_leaderboard(self.object.id)
        context['players'] = players
        context['leaderboard'] = leaderboard
        context['game'] = self.object
        return context

class CreateLeague(CreateView):
    model = League
    fields = ['name', 'is_private', 'member_can_add', 'accepts_members', 'pword']
    template_name = 'games/league_create.html'

class EditLeague(UpdateView):
    model = League
    fields = ['name', 'is_private', 'member_can_add', 'accepts_members', 'pword']
    template_name = 'games/league_edit.html'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs.get("league_id"))

# superceded by GCBV
"""def league_detail(request, league_id):
    # TODO: check if private
    now = datetime.now()
    current_player = request.user.player.id
    league = get_object_or_404(League, pk=league_id)
    is_owner = league.owned_by.id == current_player
    is_member = league.is_member(current_player)
    #if league.member_can_add and league.objects.filter(members__in=[Player.current_player]):
    if league.member_can_add and is_member:
        member_can_add = True
    else:
        member_can_add = False
    if is_owner or member_can_add:
        show_add_game = True
    else:
        show_add_game = False
    #latest_game_list = Game.objects.filter(start_date__gte=now, included_in_league=league_id).order_by('start_date')
    #previous_game_list = Game.objects.filter(end_date__lte=now, included_in_league=league_id).order_by('start_date')
    #live_game_list = Game.objects.filter(start_date__lte=now, end_date__gte=now, included_in_league=league_id).order_by('start_date')
    context = {#'latest_game_list': latest_game_list,
               #'previous_game_list': previous_game_list,
               #'live_game_list': live_game_list,
               'league': league,
               "show_add_game": show_add_game,
               "is_member": is_member,
               }
    return render(request, 'games/league_detail.html', context)
"""
# superceded by GCBV
"""def index(request):

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
"""

"""def games_index(request):
    now = datetime.now()
    latest_game_list = Game.objects.filter(start_date__gte=now, included_in_league=league_id).order_by('start_date')
    previous_game_list = Game.objects.filter(end_date__lte=now, included_in_league=league_id).order_by('start_date')
    live_game_list = Game.objects.filter(start_date__lte=now, end_date__gte=now, included_in_league=league_id).order_by('start_date')
    context = {'latest_game_list': latest_game_list, 
               'previous_game_list': previous_game_list,
               'live_game_list': live_game_list,
               'now': now
               }
    return render(request, 'games/_games_index.html', context)"""

"""def game_detail(request, game_id, league_id):
    game = get_object_or_404(Game, pk=game_id)
    players = game.get_players(league_id)
    leaderboard = Prediction.objects.get_leaderboard(game_id)
    return render(request, 'games/game_detail.html', {'game': game, 'players': players, 'leaderboard': leaderboard})"""

"""def predict(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    return render(request, 'games/predict.html', {'game': game})
"""