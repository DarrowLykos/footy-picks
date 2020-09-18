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
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


# TODO: split leagues HTML and views DRY

'''class SuperAdminView(UserPassesTestMixin, TemplateView):
    template_name = 'games/pages/superadmin.html'

    def test_func(self):
        return self.request.user.is_superuser'''

class LeagueList(LoginRequiredMixin, ListView):
    model = League
    template_name = 'games//pages/leagues_list.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        current_player = self.request.user.player.id
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        leagues_list = []
        context['member_list'] = self.model.objects.get_members_leagues(self.request.user)
        context['available_list'] = self.model.objects.get_available_leagues(self.request.user)

        return context


class LeagueDetail(DetailView):
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
        context['member_list'] = League.objects.get_members_leagues(self.request.user)
        if self.object.is_aggregate:
            context['aggregate_game'] = self.object.get_aggregate_game().id

        return context


class GameList(ListView):
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
        league = get_object_or_404(League, pk=self.kwargs.get("league_id"))
        league.update_player_points()
        players = league.get_players()
        leaderboard = Prediction.objects.get_leaderboard(league_id=league.id)
        context['players'] = players
        context['leaderboard'] = leaderboard
        context['league'] = league
        context['game'] = league
        context['title'] = "League Table"
        context['view'] = 'league'
        context['member_list'] = League.objects.get_members_leagues(self.request.user)
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
        self.object.update_player_points()
        context['players'] = players
        context['leaderboard'] = leaderboard
        context['game'] = self.object
        context['league'] = League.objects.get(pk=self.kwargs.get("league_id"))
        context['title'] = "Fixtures & Results"
        context['view'] = 'result'
        context['member_list'] = League.objects.get_members_leagues(self.request.user)
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


class PredictMatches(LoginRequiredMixin, SuccessMessageMixin, ModelFormSetView):
    model = Prediction
    template_name = "games/pages/game_detail.html"
    # form_class = PredictionFormSet
    fields = ['game', 'player', 'match', 'home_score', 'away_score', 'joker']
    success_message = "Your picks have been submitted"
    login_url = '/accounts/login/'

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
        matches = game.get_matches().filter(ko_date__gte=datetime.now())
        kwargs['extra'] = matches.count()
        return kwargs

    def get_initial(self):
        game = Game.objects.get(pk=self.kwargs.get("game_id"))
        matches = Game.objects.get(pk=self.kwargs.get("game_id")).get_matches().filter(ko_date__gte=datetime.now())
        player = Player.objects.get(user=self.request.user)
        initial_data = []
        predictions = game.get_player_predictions(self.request.user.player)
        for match in matches:
            if predictions:
                print(predictions)
                try:

                    pred = predictions.get(match=match)
                    print(pred)
                    initial_data.append({'match': match, 'game': game, 'player': player,
                                         'home_score': pred.home_score, 'away_score': pred.away_score})
                except Prediction.DoesNotExist:
                    initial_data.append({'match': match, 'game': game, 'player': player})

            else:
                initial_data.append({'match': match, 'game': game, 'player': player})

        return initial_data

    def get_queryset(self):
        game = Game.objects.get(pk=self.kwargs.get("game_id"))
        predictions = game.get_player_predictions(self.request.user.player)
        '''if predictions:
            return predictions
        else:
            return Prediction.objects.none()'''
        return Prediction.objects.none()

    def formset_valid(self, formset):
        """
           If the formset is valid redirect to the supplied URL
           """
        fs = formset.save(commit=False)
        joker_game = self.request.POST.get('joker', "")
        game = Game.objects.get(pk=self.kwargs.get("game_id"))
        predictions = game.get_player_predictions(self.request.user.player)
        if joker_game == "Please Select Joker...":
            message = messages.error(self.request, "Error: please select your joker")
            return self.render_to_response(self.get_context_data(formset=formset))
        print(self.request.POST)
        for form in fs:
            print(form)
            # print(form.has_changed())
            print(predictions.filter(match=form.match))
            preds = predictions.filter(match=form.match)
            for pred in preds:
                pred.replaced = True
                pred.save()
            if form.match.name() == joker_game:
                form.joker = True
            # form.save()
        for pred in predictions:
            print(pred.match.name())
            if joker_game != pred.match.name():
                pred.joker = False
            elif joker_game == pred.match.name():
                pred.joker = True
            pred.save()

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
        message = messages.error(self.request, "Error: Please enter a complete scoreline in the highlighted fields")
        print(self.request)
        return self.render_to_response(self.get_context_data(formset=formset))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        game = Game.objects.get(pk=self.kwargs.get("game_id"))
        context['game'] = game
        matches = game.get_matches()
        context['matches'] = matches
        league = League.objects.get(pk=self.kwargs.get("league_id"))
        players = game.get_players()
        # TODO: fix players object to show only players who have submitted predictions
        context['players'] = players
        context['league'] = league
        context['view'] = "predict"
        context['title'] = "Submit Predictions"
        context['matches_avail'] = matches.filter(ko_date__gte=datetime.now())
        context['matches_unavail'] = matches.filter(ko_date__lte=datetime.now())
        context['member_list'] = League.objects.get_members_leagues(self.request.user)
        context['player_is_member'] = game.player_is_member(self.request.user.player, league.id)
        # context['predictions'] = Prediction.objects.filter(player=self.request.user.player, game=game, replaced=False)
        context['predictions'] = game.get_player_predictions(self.request.user.player)
        context['joker'] = game.get_player_predictions(self.request.user.player).filter(joker=True)
        """for match in matches:
            initial_data.append({'match': match})
        if self.request.POST:
            context['prediction_form'] = PredictionFormSet(self.request.POST, queryset=matches)
        else:
            context['prediction_form'] = PredictionFormSet(queryset=matches)"""
        return context


class HomeView(TemplateView):
    # TODO: fix top_menu.html to match the desktop site
    template_name = 'games/pages/home.html'

class RulesView(TemplateView):
    template_name = 'games/pages/rules.html'


class PlayerView(DetailView):
    template_name = 'games/pages/player_profile.html'
    model = Player


class ContactView(TemplateView):
    template_name = 'games/pages/contact.html'


class ViewPredictions(GameDetail):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        predictions = self.object.get_player_predictions(self.kwargs.get("player_id"))
        context['predictions'] = predictions
        context['view'] = "points"
        context['title'] = "Game Performance"
        context['player'] = get_object_or_404(Player, pk=self.kwargs.get("player_id"))
        context['total_points'] = self.object.get_player_points(self.kwargs.get("player_id"))
        return context


class CreateGame(CreateView):
    model = Game
    template_name = "games/game_create.html"
    fields = ['name', 'start_date', 'end_date', 'entry_fee', 'rules', 'matches', 'public_game', ]


class EditGame(UpdateView):
    model = Game
    template_name = "games/game_edit.html"
