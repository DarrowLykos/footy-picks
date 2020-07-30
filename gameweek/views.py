from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, get_list_or_404
from datetime import datetime
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView, TemplateView
from player.models import Player
from .models import Game, League, Prediction
from player.models import Player
from .forms import PredictionFormSet, PredictionForm
from django.contrib.auth.models import User
from extra_views import ModelFormSetView, SuccessMessageMixin
from crispy_forms.helper import FormHelper
from django.urls import path, re_path, include, reverse_lazy
from django.contrib import messages
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin


# TODO: split leagues HTML and views DRY

class LeagueList(LoginRequiredMixin, ListView):
    model = League
    template_name = 'games//pages/leagues_list.html'

    def get_context_data(self, **kwargs):
        current_player = self.request.user.player.id
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        leagues_list = []
        context['member_list'] = self.model.objects.get_members_leagues(self.request.user)
        context['available_list'] = self.model.objects.get_available_leagues(self.request.user)

        return context


class LeagueDetail(LoginRequiredMixin, DetailView):
    model = League
    template_name = 'games/pages/league_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs.get("league_id"))

    def get_context_data(self, **kwargs):
        # try:
        current_player = self.request.user.player.id
        # except AttributeError:
        # current_player = None
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        is_owner = self.object.is_owner(current_player)
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
        leaderboard = Prediction.objects.get_leaderboard(league_id=self.object.id)
        context['leaderboard'] = leaderboard
        if self.object.is_aggregate:
            context['aggregate_game'] = self.object.get_aggregate_game().id

        return context


class GameList(LoginRequiredMixin, ListView):
    model = Game
    template_name = 'games/pages/game_detail.html'

    def get_object(self, queryset=None):
        queryset = get_list_or_404(self.model.objects.filter(included_in_league=self.kwargs.get("league_id")))
        return queryset

    def get_context_data(self, **kwargs):
        try:
            current_player = self.user.player.id
        except AttributeError:
            current_player = None
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        league = League.objects.get(pk=self.kwargs.get("league_id"))
        players = league.get_players()
        leaderboard = Prediction.objects.get_leaderboard(league_id=league.id)
        context['players'] = players
        context['leaderboard'] = leaderboard
        context['league'] = league
        context['game'] = league
        context['title'] = "League Info"
        context['view'] = 'league'
        # context['live_games'] = league.games.filter(is_live=True)
        return context


class GameDetail(DetailView):
    model = Game
    template_name = 'games/pages/game_detail.html'

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
        players = self.object.get_players()
        leaderboard = Prediction.objects.get_leaderboard(game_id=self.object.id)
        context['players'] = players
        context['leaderboard'] = leaderboard
        context['game'] = self.object
        context['league'] = League.objects.get(pk=self.kwargs.get("league_id"))
        context['title'] = "Results"
        context['view'] = 'result'
        matches = self.object.get_matches()
        context['matches'] = matches
        return context

class CreateLeague(CreateView):
    model = League
    fields = ['name', 'is_private', 'member_can_add', 'accepts_members', 'pword']
    template_name = 'games/league_create.html'

    #TODO : redirect once submitted

# TODO: only allow owner to edit
class EditLeague(UpdateView):
    model = League
    fields = ['name', 'is_private', 'member_can_add', 'accepts_members', 'pword']
    template_name = 'games/league_edit.html'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs.get("league_id"))

class JoinLeague(FormView):
    #TODO: create form to use
    model = League
    template_name = 'games/league_join.html'
    fields = ['pword']
    context_object_name = "league"

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs.get("league_id"))

    #TODO : error if password is wrong
    #TODO : error if not accepting members

    # TODO : validate password entered and add member


class LeaveLeague(FormView):
    # TODO: create form to use
    model = League
    template_name = "games/league_leave.html"

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs.get("league_id"))


# class PredictConfirmation(View):
# template_name = "games/prediction_confirmation.html"


class PredictMatches(SuccessMessageMixin, ModelFormSetView):
    model = Prediction
    template_name = "games/pages/game_detail.html"
    # form_class = PredictionFormSet
    fields = ['game', 'player', 'match', 'home_score', 'away_score', 'joker']
    success_message = "Your picks have been submitted"

    def get_success_url(self):
        return reverse_lazy('picks_pages:game_detail',
                            kwargs={'game_id': self.kwargs['game_id'], 'league_id': self.kwargs['league_id']})

    def get_formset_kwargs(self):
        kwargs = super(PredictMatches, self).get_formset_kwargs()
        kwargs['form_kwargs'] = ({'empty_permitted': False})
        return kwargs

    def get_factory_kwargs(self):
        kwargs = super(PredictMatches, self).get_factory_kwargs()
        game = Game.objects.get(pk=self.kwargs.get("game_id"))
        matches = game.get_matches()
        kwargs['extra'] = matches.count()
        return kwargs

    def get_initial(self):
        game = Game.objects.get(pk=self.kwargs.get("game_id"))
        matches = Game.objects.get(pk=self.kwargs.get("game_id")).get_matches()
        player = Player.objects.get(user=self.request.user)
        initial_data = []
        for match in matches:
            initial_data.append({'match': match, 'game': game, 'player': player})

        return initial_data

    def get_queryset(self):
        game = Game.objects.get(pk=self.kwargs.get("game_id"))
        predictions = Prediction.objects.filter(player=self.request.user.player, game=game)
        return Prediction.objects.none()

    def formset_valid(self, formset):
        """
           If the formset is valid redirect to the supplied URL
           """
        fs = formset.save(commit=False)
        joker_game = self.request.POST.get('joker', "")
        for form in fs:
            if form.match.name() == joker_game:
                form.joker = True
            # form.save()
        formset.save(commit=True)
        # for prediction in predictions:
        # prediction.instance = self.object
        #    prediction.player = Player.objects.get(user=self.request.user)  # use your own profile here
        #   prediction.game = Game.objects.get(pk=self.kwargs.get("game_id"))
        # prediction.match = Match.objects.get(pk=self.kwargs.get("match_id"))
        #    prediction.save()
        message = messages.success(self.request, "Picks Submitted")
        return HttpResponseRedirect(self.get_success_url(), {'message_disp': message})

    def formset_invalid(self, formset):
        """
        If the formset is invalid, re-render the context data with the
        data-filled formset and errors.
        """
        message = messages.error(self.request, "Error: please check your picks")
        return self.render_to_response(self.get_context_data(formset=formset))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        game = Game.objects.get(pk=self.kwargs.get("game_id"))
        context['game'] = game
        matches = game.get_matches()
        context['matches'] = matches
        players = game.get_players()
        context['players'] = players
        context['league'] = League.objects.get(pk=self.kwargs.get("league_id"))
        context['view'] = "predict"
        context['title'] = "Submit Predictions"
        context['matches_avail'] = matches.filter(ko_date__gte=datetime.now())
        """for match in matches:
            initial_data.append({'match': match})
        if self.request.POST:
            context['prediction_form'] = PredictionFormSet(self.request.POST, queryset=matches)
        else:
            context['prediction_form'] = PredictionFormSet(queryset=matches)"""
        return context


"""class PredictMatches(CreateView):

    # TODO: allow user to reflect predictions across all leagues
    model = Prediction
    template_name = "games/_predictions.html"
    fields = ['game', 'player', 'match', 'home_score', 'away_score', 'joker']
    #form_class = PredictionForm

    #TODO: tidy up html layout
    # TODO: figure out how to add read only fields and prepopulate them
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        game = Game.objects.get(pk=self.kwargs.get("game_id"))
        context['game'] = game
        matches = game.get_matches()
        context['matches'] = matches
        initial_data = []
        for match in matches:
            initial_data.append({'match': match})
        if self.request.POST:
            prediction_formset = PredictionFormSet(self.request.POST, queryset=matches)
            context['prediction_form'] = prediction_formset
            if prediction_formset.is_valid():
                context['prediction_form'] = prediction_formset
                # Note - we are passing the education_formset to form_valid. If you had more formsets
                # you would pass these as well.
                return self.form_valid(prediction_formset)
        else:
            context['prediction_form'] = PredictionFormSet(queryset=matches)
        return context

    def post(self, request, *args, **kwargs):
        game = Game.objects.get(pk=self.kwargs.get("game_id"))
        matches = game.get_matches()
        form = self.get_form()
        # Add as many formsets here as you want
        prediction_form = PredictionFormSet(request.POST)
        # Now validate both the form and any formsets
        if form.is_valid() and prediction_form.is_valid():
            # Note - we are passing the education_formset to form_valid. If you had more formsets
            # you would pass these as well.
            return self.form_valid(form, prediction_form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, prediction_form):
        predictions = prediction_form.save(commit=False)
        for prediction in predictions:
            prediction.instance = self.object
            prediction.player = Player.objects.get(user=self.request.user)  # use your own profile here
            prediction.game = Game.objects.get(pk=self.kwargs.get("game_id"))
            # prediction.match = Match.objects.get(pk=self.kwargs.get("match_id"))
            prediction.save()
        #prediction = form.save(commit=False)

        #prediction.save()
        return HttpResponseRedirect(self.get_success_url())"""


class HomeView(TemplateView):
    template_name = 'games/pages/home.html'


class RulesView(TemplateView):
    template_name = 'games/pages/rules.html'


class ContactView(TemplateView):
    template_name = 'games/pages/contact.html'


class ViewPredictions(UpdateView):
    model = Prediction
    template_name = "games/game_predict_detail.html"


class CreateGame(CreateView):
    model = Game
    template_name = "games/game_create.html"
    fields = ['name', 'start_date', 'end_date', 'entry_fee', 'rules', 'matches', 'public_game', ]

class EditGame(UpdateView):
    model = Game
    template_name = "games/game_edit.html"

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
    return render(request, 'games/leagues_list.html', context)
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
    return render(request, 'games/_predictions.html', {'game': game})
"""
