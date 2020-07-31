from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

# Create your models here.
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
    thumbnail = models.ImageField('Logo', blank=True, upload_to="Competition logos/")

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=3)
    thumbnail = models.ImageField('Logo', upload_to="Team logos/")
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
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches",
                                  related_query_name="home_match")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches",
                                  related_query_name="away_match")
    ko_date = models.DateTimeField('Kick Off')
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    # TODO: filter competition by matching home_team.competition and away_team.competition values
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    penalties = models.BooleanField(default=False)
    extra_time = models.BooleanField(default=False)
    postponed = models.BooleanField(default=False)
    result = models.CharField(max_length=8, choices=RESULT_CHOICES, default="ToPlay")

    # TODO: something wrong with timezone
    def name(self):
        return self.home_team.name + " vs " + self.away_team.name

    def __str__(self):
        return self.name() + " | " + self.competition.name + " | " + self.ko_date.strftime('%d %b %Y %H:%M')

    class Meta:
        verbose_name = "Match"
        verbose_name_plural = "Matches"

    def final_score(self):
        if self.result == "ToPlay":
            return "-"
        else:
            return str(self.home_score) + "-" + str(self.away_score)

    def status(self):
        current_datetime = datetime.now()
        ko_datetime = timezone.make_aware(self.ko_date)
        full_time = self.ko_date + timedelta(hours=1, minutes=45)
        extra_time = self.ko_date + timedelta(hours=2, minutes=30)
        penalties = self.ko_date + timedelta(hours=3)
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
        elif current_datetime < self.ko_date:
            return status[1]
        elif current_datetime < full_time:
            return status[2]
        elif current_datetime > full_time and (self.extra_time and current_datetime < extra_time):
            return status[4]
        elif current_datetime > extra_time and (self.penalties and current_datetime < penalties):
            return status[5]
        elif current_datetime > full_time:
            return status[3]

    def kick_off(self):
        return self.ko_date.strftime('%H:%M')

    def matchday(self):
        return self.ko_date.strftime('%d %b %Y')
