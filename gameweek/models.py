from django.db import models
from player.models import Player
# from player.models import Profile
from rule.models import Rule
# from datetime import datetime
from django.utils import timezone
import random
import string
from picks import calculate_score

# from django.contrib.auth.models import User

now = timezone.now()

def randomised_password():
    letters = string.ascii_lowercase
    rand_pword = ''.join(random.choice(letters) for i in range(8))
    return rand_pword

COUNTRY_CHOICES = (
    ("ENG", "England"),
    ("WOR", "World"),
    ("EUR", "Europe"),
    ("SCO", "Scotland"),
    ("ESP", "Spain"),
    ("FRA", "France"),
    ("GER", "Germany")
)

class Competition(models.Model):
    COMP_CHOICES = (
        ("DOL", "Domestic League"),
        ("DOC", "Domestic Cup"),
        ("INC", "International Cup"),
        ("DOF", "Domestic Friendly"),
        ("INF", "International Friendly"),
        ("INQ", "International Qualifiers"),
    )
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, default="ENG")
    comp_type = models.CharField("Competition Type", max_length=3, choices=COMP_CHOICES, default="DOL")
    thumbnail = models.ImageField('Logo', blank=True, upload_to="Media/Competition logos/")

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=3)
    thumbnail = models.ImageField('Logo', blank=True, upload_to="Media/Team logos/")
    country = models.CharField(max_length=3, choices=COUNTRY_CHOICES, default="ENG")
    competitions = models.ManyToManyField(Competition)

    def __str__(self):
        return self.name


class Match(models.Model):
    RESULT_CHOICES = (
        ("Home90", "Home win in 90 minutes"),
        ("Draw90", "Draw in 90 minutes"),
        ("Away90", "Away win in 90 minutes"),
        ("Home120", "Home win in Extra Time"),
        ("Away120", "Away win in Extra Time"),
        ("HomePens", "Home win after Penalties"),
        ("AwayPens", "Away win after Penalties"),
        ("ToPlay", "Still to be played"),
    )
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches", related_query_name="home_match")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches", related_query_name="away_match")
    ko_date = models.DateTimeField('Kick Off')
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    #TODO: filter competition by matching home_team.competition and away_team.competition values
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    penalties = models.BooleanField(default=False)
    extra_time = models.BooleanField(default=False)
    postponed = models.BooleanField(default=False)
    result = models.CharField(max_length=8, choices=RESULT_CHOICES, default="ToPlay")

    def name(self):
        return self.home_team.name + " vs " + self.away_team.name + " | " + self.competition.name + " | " \
               + self.ko_date.strftime('%d %b %Y %H:%M')

    def __str__(self):
        return self.name()

    class Meta:
        verbose_name = "Match"
        verbose_name_plural = "Matches"

    def kick_off(self):
        return self.ko_date.strftime('%H:%M')

    def matchday(self):
        return self.ko_date.strftime('%d %b %Y')

    def final_score(self):
        return str(self.home_score) + "-" + str(self.away_score)

    def status(self):
        current_datetime = timezone.now()
        ko_datetime = timezone.make_aware(self.ko_date)
        full_time = ko_datetime + timezone.timedelta(hours=1, minutes=45)
        extra_time = ko_datetime + timezone.timedelta(hours=2, minutes=30)
        penalties = ko_datetime + timezone.timedelta(hours=3)
        status = {1: "Upcoming",
                  2: "In play",
                  3: "Full time",
                  4: "Extra Time",
                  5: "Penalties",
                  6: "Postponed",
                  7: "Abandoned"
                  }
        if self.postponed:
            return status[6]
        elif current_datetime > self.ko_date:
            return status[1]
        elif current_datetime < full_time:
            return status[2]
        elif current_datetime > full_time and (self.extra_time and current_datetime < extra_time):
            return status[4]
        elif current_datetime > extra_time and (self.penalties and current_datetime < penalties):
            return status[5]
        elif current_datetime > full_time:
            return status[3]


class MatchProxy(Match):
    class Meta:
        proxy = True
        verbose_name = "Match (Create)"
        verbose_name_plural = "Matches (Create)"


class Game(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    matches = models.ManyToManyField(Match, blank=True, null=True, related_name="games", related_query_name="game")
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2)
    rules = models.ForeignKey(Rule, on_delete=models.CASCADE)
    # prize_pool = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    _hidden = models.BooleanField(default=False)
    available = models.BooleanField(default=False)
    public_game = models.BooleanField(default=True)
    # created_by = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="game_created_by")
    # owned_by = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="game_owned_by")
    pword = models.CharField(max_length=100, default=randomised_password)
    is_super_game = models.BooleanField(default=False)
    aggregated_games = models.ManyToManyField("Game", blank=True, null=True, related_query_name="super_game", related_name="super_games")
    #predictions = models.ManyToManyField(Match.predictions, through=matches)

    class Meta:
        ordering = ('-start_date', )
    def prize_pool(self):
        pass

    def get_matches(self):
        if self.is_super_game:
            self.aggregated_games.all()
        else:
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

    def __str__(self):
        return self.name

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

    def get_players(self):
        return self.get_predictions().players.all()

class Prediction(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    home_score = models.IntegerField(default=0, null=True, blank=True)
    away_score = models.IntegerField(default=0, null=True, blank=True)
    joker = models.BooleanField(default=False)
    submit_date_time = models.DateTimeField(auto_now=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="predictions", related_query_name="prediction")

    def valid(self):
        return self.submit_date_time <= self.match.ko_date

    def __str__(self):
        return self.player.user.get_full_name() + "|" + str(self.match) + "|" + self.predicted_score()

    def rules(self):
        return self.game.rules

    def points(self):
        points = calculate_score(predicted_score=self.predicted_score(),
                                  actual_score=self.actual_score(),
                                  joker=self.joker,
                                  rule_set=self.rules().__dict__
                                  )
        return str(points)

    def predicted_score(self):
        return str(self.home_score) + "-" + str(self.away_score)

    def actual_score(self):
        return self.match.final_score()