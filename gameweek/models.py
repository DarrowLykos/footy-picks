from django.db import models
from player.models import Player
from team.models import Match
# from player.models import Profile
from rule.models import Rule
from datetime import datetime, timedelta
from django.utils import timezone
import random
import string
from picks import calculate_score
from django.db.models import Count, Sum, Avg, Max, Min
from django.db.models import F
# from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator
import praw

now = timezone.now()

def randomised_password():
    letters = string.ascii_lowercase
    rand_pword = ''.join(random.choice(letters) for i in range(8))
    return rand_pword

class Game(models.Model):
    name = models.CharField(max_length=12)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    matches = models.ManyToManyField(Match, blank=True, related_name="games", related_query_name="game")
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2)
    # rules = models.ForeignKey(Rule, on_delete=models.CASCADE)
    # prize_pool = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    _hidden = models.BooleanField(default=False)
    available = models.BooleanField(default=False)
    public_game = models.BooleanField(default=True)
    created_by = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="games_created_by")
    owned_by = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="games_owned_by")
    last_update = models.DateTimeField(auto_now=True)
    # pword = models.CharField(max_length=100, default=randomised_password)
    # is_super_game = models.BooleanField(default=False)
    # aggregated_games = models.ManyToManyField("Game", blank=True, null=True, related_query_name="super_game", related_name="super_games")
    #predictions = models.ManyToManyField(Match.predictions, through=matches)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-start_date',)

    def prize_pool(self):
        pass

    def rules(self):
        return self.leagues_included_in.all()[0].rules

    # def get_leagues(self):
    #     return self.leagues_included_in.all()

    def get_position(self, player_id):
        # tally up points per match, per player
        # determine rank of player_id
        # return position
        pass

    def get_matches(self):
        return self.matches.all().order_by('ko_date')

    def total_matches(self):
        return self.matches.all().count()

    def completed_matches(self):
        #TODO: add filter for end_date of matches
        return self.matches.all().count()

    def to_play_matches(self):
        #TODO: add filter for start date of matches
        return self.matches.all().count()

    def in_play_matches(self):
        #TODO: add filter for live matches
        return self.matches.all().count()

    def time_until_start(self):
        return self.start_date - now

    def time_until_end(self):
        return self.end_date - now

    def is_private(self):
        if self.public_game == False:
            return True

    def is_public(self):
        if self.public_game:
            return True

    def is_available(self):
        if self.available:
            return True
        else:
            return False

    def validate_dates(self):
        if self.end_date > self.start_date:
            return True
        else:
            return False

    def is_live(self):
        if self.end_date == None:
            return False
        else:
            return self.end_date > now and now > self.start_date

    def is_upcoming(self):
        if self.start_date == None:
            return False
        else:
            return self.start_date > now

    def is_finished(self):
        if self.end_date == None:
            return False
        else:
            return self.end_date < now

    def status(self):
        if self.is_live():
            return "live"
        elif self.is_finished():
            return "finished"
        else:
            return "to play"

    def get_predictions(self):
        return self.predictions.all()

    def get_players(self):
        predictions = self.get_predictions()
        return predictions.select_related('player').values('player').annotate(
            name=F('player__user__username')).distinct().order_by('player')

    def get_league_players(self, league_id):
        return self.leagues_included_in.filter(pk=league_id)[0].get_players().order_by('user')

    def get_player_predictions(self, player_id, include_invalid=False):
        player_predictions = self.get_predictions().filter(player=player_id, replaced=include_invalid)
        return player_predictions

    def update_player_points(self):
        rules = self.rules()
        preds = self.get_predictions().prefetch_related('match').exclude(final=True, replaced=True)
        for pred in preds:
            pred.get_points(rules)

    def get_player_points(self, player_id):
        predictions = self.get_predictions().filter(player_id=player_id).prefetch_related('match')
        # print(predictions)
        points = predictions.values('player').annotate(total_points=Sum('points'))
        # print(points)
        try:
            points = points[0]['total_points']
            return points
        except:
            return 0

    def player_is_member(self, player_id, league_id):
        if player_id in self.leagues_included_in.get(pk=league_id).members.all():
            return True
        else:
            return False

    def populate_matches(self, start_date=None, end_date=None, max_matches=10, competition=None, **kwargs):
        if start_date == None:
            start_date = self.start_date
        if end_date == None:
            end_date = self.end_date
        matches = Match.objects.filter(ko_date__gte=start_date, ko_date__lte=end_date).order_by('?')
        existing_matches = self.matches.all()
        counter = existing_matches.count()
        for match in matches:
            if not match in existing_matches and counter < max_matches:
                if competition == None or match.competition == competition:
                    self.matches.add(match)
                    counter += 1

    def get_reddit_predictions(self, comments_id):
        get_reddit_predictions(comments_id, self.id)

    def leaderboard(self, filter_top=False):
        lb = self.predictions.filter(game_id=self.id).values('player').annotate(total_points=Sum('points')).order_by(
            '-points')
        if filter_top == False:
            return lb
        else:
            return lb[:filter_top]


class LeagueManager(models.Manager):
    def get_members_leagues(self, user):
        return self.filter(members__in=[user.player.id]).order_by('name')

    def get_available_leagues(self, user):
        return self.exclude(members__in=[user.player.id]).order_by('name')


class League(models.Model):
    name = models.CharField(max_length=100)
    pword = models.CharField(max_length=100, default=randomised_password)
    # TODO: add creator by default to members
    members = models.ManyToManyField(Player, blank=True, related_name="leagues_member_of",
                                     related_query_name="member_of_league")
    games = models.ManyToManyField(Game, blank=True, related_query_name="included_in_league",
                                   related_name="leagues_included_in")
    is_private = models.BooleanField(default=False)
    # TODO: default owner to created by
    created_by = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name="created_leagues", related_query_name="league_creator")
    owned_by = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL, related_name="owned_leagues",
                                 related_query_name="league_owner")
    member_can_add = models.BooleanField("Members can add games", default=False)
    accepts_members = models.BooleanField("Accepts new members", default=True)
    is_aggregate = models.BooleanField(default=False)
    rules = models.ForeignKey(Rule, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    objects = LeagueManager()
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    # TODO: get this save model working on auto-populating fields
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.created_by = request.user
            obj.owned_by = request.user
        super().save_model(request, obj, form, change)

    def is_member(self, user_id):
        if self.members.filter(id=user_id).exists():
            return True
        else:
            return False

    def is_owner(self, user_id):
        if self.owned_by.id == user_id:
            return True
        else:
            return False

    def get_players(self):
        return self.members.all()

    def total_players(self):
        return self.members.all().count()

    def get_games(self):
        return self.games.all()

    def get_aggregate_game(self):
        games = self.get_games()
        return games[0]

    def change_password(self):
        return randomised_password()

    def is_live(self):
        if self.end_date == None:
            return False
        else:
            return self.end_date > now and now > self.start_date

    def is_upcoming(self):
        if self.start_date == None:
            return False
        else:
            return self.start_date > now

    def is_finished(self):
        if self.end_date == None:
            return False
        else:
            return self.end_date < now

    def status(self):
        if self.is_live():
            return "live"
        elif self.is_finished():
            return "finished"
        else:
            return "to play"

    def update_player_points(self):
        games = self.get_games()

        for game in games:
            game.update_player_points()

class PredictionManager(models.Manager):
    def game_leaderboard(self, game_id):
        lb = self.select_related('player') \
            .filter(game_id__in=game_id) \
            .values('player', ) \
            .annotate(name=F('player__user__username'),
                      total_points=Sum('points'),
                      total_games=Count('game', distinct=True),
                      average_points=Avg('points'),
                      max_points=Max('points'),
                      min_points=Min('points'),
                      ) \
            .order_by('-total_points')
        # .values('name', '_total_points', '_total_games')
        # .annotate(total_points=F('_total_points'), total_games=F('_total_games'))

        return lb

    def get_leaderboard(self, **kwargs):
        if 'game_id' in kwargs:
            return self.game_leaderboard([kwargs['game_id']])
        elif 'league_id' in kwargs:
            league = League.objects.get(pk=kwargs['league_id'])
            game_ids = []
            for game in league.get_games():
                game_ids.append(game.id)
            return self.game_leaderboard(game_ids)


class Prediction(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    home_score = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    away_score = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    joker = models.BooleanField(default=False)
    submit_date_time = models.DateTimeField(auto_now_add=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="predictions",
                             related_query_name="prediction")
    points = models.IntegerField(default=0, null=True, blank=True)
    objects = PredictionManager()
    replaced = models.BooleanField(default=False)
    valid_override = models.BooleanField(default=False)
    final = models.BooleanField(default=False)

    def __str__(self):
        return self.player.user.get_full_name() + "|" + str(self.match) + "|" + self.predicted_score()

    def valid(self):
        if not self.replaced and (self.submit_date_time <= self.match.ko_date or self.valid_override):
            return True
        else:
            return False

    def rules(self):
        return self.game.rules()

    def get_points(self, rules, force_update=False):
        if self.final and not force_update:
            return self.points
        elif self.actual_score() == "-" or self.replaced:
            return 0
        else:
            points = calculate_score(predicted_score=self.predicted_score(),
                                     actual_score=self.actual_score(),
                                     joker=self.joker,
                                     rule_set=rules.__dict__
                                     )
            if self.match_finished():
                self.final = True
                self.save()
            if self.valid():
                self.points = points
                self.save()
                return str(points)
            else:
                return 0

    def predicted_score(self):
        return str(self.home_score) + "-" + str(self.away_score)

    def actual_score(self):
        return self.match.final_score()

    def match_finished(self):
        if self.match.status == "Match Finished":
            return True
        else:
            return False

    """def aggregated_game_points(game_id):
        return Prediction.objects.filter(game_id=game_id).values('player').annotate(total_points=Sum('points'))"""

    """def get_player_game_points(self, game_id, player_id):
        agg_points = self.aggregated_game_points(game_id)
        player_points = agg_points.get(player_id=player_id)
        return player_points"""
