from django.db import models
from player.models import Player
from team.models import Match
# from player.models import Profile
from rule.models import Rule
# from datetime import datetime
from django.utils import timezone
import random
import string
from picks import calculate_score
from django.db.models import Count, Sum
from django.db.models import F
# from django.contrib.auth.models import User
from django.db import models

now = timezone.now()

def randomised_password():
    letters = string.ascii_lowercase
    rand_pword = ''.join(random.choice(letters) for i in range(8))
    return rand_pword

class Game(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    matches = models.ManyToManyField(Match, blank=True, related_name="games", related_query_name="game")
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2)
    rules = models.ForeignKey(Rule, on_delete=models.CASCADE)
    # prize_pool = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    _hidden = models.BooleanField(default=False)
    available = models.BooleanField(default=False)
    public_game = models.BooleanField(default=True)
    created_by = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="games_created_by")
    owned_by = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="games_owned_by")
    # pword = models.CharField(max_length=100, default=randomised_password)
    # is_super_game = models.BooleanField(default=False)
    # aggregated_games = models.ManyToManyField("Game", blank=True, null=True, related_query_name="super_game", related_name="super_games")
    #predictions = models.ManyToManyField(Match.predictions, through=matches)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-start_date', )

    def prize_pool(self):
        pass

    # def get_leagues(self):
    #     return self.leagues_included_in.all()

    def get_position(self, player_id):
        # tally up points per match, per player
        # determine rank of player_id
        # return position
        pass

    def get_matches(self):
        return self.matches.all()

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
            return self.end_date > now > self.start_date

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

    def get_players(self, league_id):
        return self.leagues_included_in.filter(pk=league_id)[0].get_players().order_by('user')

    # TODO: output leaderboard of aggregated scores
    def leaderboard(self, filter_top=False):
        lb = self.predictions.filter(game_id=self.id).values('player').annotate(total_points=Sum('points')).order_by('-points')
        if filter_top == False:
            return lb
        else:
            return lb[:filter_top]

class League(models.Model):
    name = models.CharField(max_length=100)
    pword = models.CharField(max_length=100, default=randomised_password)
    # TODO: add creator by default to members
    members = models.ManyToManyField(Player, blank=True, related_name="leagues_member_of", related_query_name="member_of_league")
    games = models.ManyToManyField(Game, blank=True, related_query_name="included_in_league", related_name="leagues_included_in")
    is_private = models.BooleanField(default=False)
    # TODO: default owner to created by
    created_by = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_leagues", related_query_name="league_creator")
    owned_by = models.ForeignKey(Player, null=True, blank=True,  on_delete=models.SET_NULL, related_name="owned_leagues", related_query_name="league_owner")
    member_can_add = models.BooleanField("Members can add games", default=False)
    accepts_members = models.BooleanField("Accepts new members", default=True)

    def __str__(self):
        return self.name

    #TODO: get this save model working on auto-populating fields
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

    def change_password(self):
        return randomised_password()

class PredictionManager(models.Manager):
    def get_leaderboard(self, game_id):
        lb = self.select_related(
            'player').filter(
            game_id=game_id).values(
            'player').annotate(
            name=F('player__user__username'), total_points=Sum('points')).order_by('-total_points')
        return lb

class Prediction(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    home_score = models.IntegerField(default=0, null=True, blank=True)
    away_score = models.IntegerField(default=0, null=True, blank=True)
    joker = models.BooleanField(default=False)
    submit_date_time = models.DateTimeField(auto_now=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="predictions", related_query_name="prediction")
    points = models.IntegerField(default=0)
    objects = PredictionManager()

    def valid(self):
        return self.submit_date_time <= self.match.ko_date

    def __str__(self):
        return self.player.user.get_full_name() + "|" + str(self.match) + "|" + self.predicted_score()

    def rules(self):
        return self.game.rules

    def get_points(self):
        if self.actual_score() == "N/A":
            return 0
        else:
            points = calculate_score(predicted_score=self.predicted_score(),
                                      actual_score=self.actual_score(),
                                      joker=self.joker,
                                      rule_set=self.rules().__dict__
                                      )
            self.points = points
            return str(points)

    def predicted_score(self):
        return str(self.home_score) + "-" + str(self.away_score)

    def actual_score(self):
        return self.match.final_score()




    """def aggregated_game_points(game_id):
        return Prediction.objects.filter(game_id=game_id).values('player').annotate(total_points=Sum('points'))"""

    """def get_player_game_points(self, game_id, player_id):
        agg_points = self.aggregated_game_points(game_id)
        player_points = agg_points.get(player_id=player_id)
        return player_points"""