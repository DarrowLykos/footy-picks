from django.db import models
from player.models import Player
#from player.models import Profile
from rule.models import Rule
#from datetime import datetime
from django.utils import timezone
#from django.contrib.auth.models import User

now = timezone.now()

COUNTRY_CHOICES =(
        ("ENG", "England"),
        ("WOR", "World"),
        ("EUR", "Europe"),
        ("SCO", "Scotland"),
        ("ESP", "Spain"), 
        ("FRA", "France"),
        ("GER", "Germany")
    )

class Competition(models.Model):
    COMP_CHOICES =( 
            ("Domestic League", "Domestic League"), 
            ("Domestic Cup", "Domestic Cup"), 
            ("International Cup", "International Cup"), 
            ("Domestic Friendly", "Domestic Friendly"), 
            ("International Friendly", "International Friendly"), 
            ("International Qualifiers", "International Qualifiers"), 
        ) 
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, default="ENG")
    comp_type = models.CharField("Competition Type", max_length=100, choices=COMP_CHOICES, default="Domestic League")
    
    def __str__(self):
        return self.name
    
class Team(models.Model):
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=3)
    thumbnail = models.ImageField('Logo', blank=True, upload_to="Media/Team logos/")
    country = models.CharField(max_length=200, choices=COUNTRY_CHOICES, default="ENG")
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
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_team_name")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_team_name")
    #home_team = models.CharField(max_length=200)
    #away_team = models.CharField(max_length=200)
    ko_datetime = models.DateTimeField('Kick Off')
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    penalties = models.BooleanField(default=False)
    extra_time = models.BooleanField(default=False)
    postponed = models.BooleanField(default=False)
    result = models.CharField(max_length=8, choices=RESULT_CHOICES, default="ToPlay")
    
    def name(self):
        return self.home_team.name + " vs " + self.away_team.name + " | " + self.competition.name + " | " + self.ko_datetime.strftime('%d %b %Y %H:%M')
    
    def __str__(self):
        return self.name()
    
    class Meta:
        verbose_name = "Match"
        verbose_name_plural = "Matches"
    
    def kick_off(self):
        return self.ko_datetime.strftime('%H:%M')
    
    def matchday(self):
        return self.ko_datetime.strftime('%d %b %Y')
    
    def final_score(self):
        return str(self.home_score) + "-" + str(self.away_score)
    
    def status(self):
        current_datetime = timezone.now()
        ko_datetime = timezone.make_aware(self.ko_datetime)
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
        elif current_datetime > self.ko_datetime:
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
           
class Prediction(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    home_score = models.IntegerField(default=0, null=True, blank=True)
    away_score = models.IntegerField(default=0, null=True, blank=True)
    joker = models.BooleanField(default=False)
    submit_date_time = models.DateTimeField(auto_now_add=True)
    
    def valid(self):
        return self.submit_date_time <= self.match.ko_datetime  
    
    def __str__(self):
        return  "'s Prediction"
    
    def points(self):
        return 0
    
    def predicted_score(self):
        return self.home_score + "-" + self.away_score
    
class Game(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    matches = models.ManyToManyField(Match, blank=True, null=True)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2)
    rules = models.ForeignKey(Rule, on_delete=models.CASCADE)
    prize_pool = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    _hidden = models.BooleanField(default=False)
    available = models.BooleanField(default=False)
    #created_by = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="created_by")
    #owned_by = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="owned_by")
    #password = models.CharField(max_length=100)
    aggregated_games = models.ManyToManyField("Game", blank=True, null=True) 
    
    
    def __str__(self):
        return self.name
    
    def validate_dates(self):
        if self.end_date > self.start_date :
            return True
        else:
            return False
        
    def is_live(self):
        return (self.end_date >= now and self.start_date <= now)
    
    def is_upcoming(self):
        return self.start_date > now
    
    def is_finished(self):
        return self.end_date < now