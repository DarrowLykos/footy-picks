from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import requests
import dateutil.parser
import pytz

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
    api_id = models.IntegerField(null=True)

    def __str__(self):
        return self.name

    def create_matches(self, round_id, season):
        url = f"https://www.thesportsdb.com/api/v1/json/1/eventsround.php?id={self.api_id}&r={round_id}&s={season}"
        r = requests.get(url).json()
        for event in r['events']:
            print(event)
            home_team_id = event['idHomeTeam']
            away_team_id = event['idAwayTeam']
            # ko_date = event['strTimestamp']
            ko_t = event['strTime']
            ko_d = event['dateEvent']
            ko_date = datetime.strptime(f"{ko_d} {ko_t}", "%Y-%m-%d %H:%M:%S")
            comp_id = event['idLeague']
            match_api_id = event['idEvent']
            try:
                home_team = Team.objects.get(api_id=home_team_id)
            except:
                print('Creating home team')
                home_team = Team(name=event['strHomeTeam'], short_name=event['strHomeTeam'][:3].upper(),
                                 api_id=home_team_id, country=event['strCountry'])
                home_team.save()
                home_team.competitions.add(self)
                home_team = Team.objects.get(api_id=home_team_id)
            try:
                away_team = Team.objects.get(api_id=away_team_id)
            except:
                print('Creating away team')
                away_team = Team(name=event['strAwayTeam'], short_name=event['strAwayTeam'][:3].upper(),
                                 api_id=away_team_id,
                                 country=event['strCountry'])
                away_team.save()
                away_team.competitions.add(self)
                away_team = Team.objects.get(api_id=away_team_id)
            comp = self
            if Match.objects.filter(api_id=match_api_id).count() == 0:
                print('Creating match')
                match = Match(home_team=home_team, away_team=away_team, ko_date=ko_date, competition=comp,
                              api_id=match_api_id, last_api=datetime.now())
                match.save()

class Team(models.Model):
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=3)
    thumbnail = models.ImageField('Logo', upload_to="Team logos/")
    country = models.CharField(max_length=3, choices=COUNTRY_CHOICES, default="ENG")
    competitions = models.ManyToManyField(Competition)
    api_id = models.IntegerField(null=True)

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
    status = models.CharField(max_length=20, default="Not Started")
    result = models.CharField(max_length=8, choices=RESULT_CHOICES, default="ToPlay")
    api_id = models.IntegerField(null=True)
    last_api = models.DateTimeField()

    class Meta:
        ordering = ('-ko_date',)

    # TODO: something wrong with timezone
    def name(self):
        return self.home_team.name + " vs " + self.away_team.name

    def short_name(self):
        return self.home_team.short_name + " vs " + self.away_team.short_name

    def __str__(self):
        return self.name() + " | " + self.competition.name + " | " + self.ko_date.strftime('%d %b %Y %H:%M')

    class Meta:
        verbose_name = "Match"
        verbose_name_plural = "Matches"

    def final_score(self):
        if self.status == "Match Postponed":
            return "Postponed"
        elif self.status != "Match Finished":
            return "-"
        else:
            return str(self.home_score) + "-" + str(self.away_score)

    '''def status(self):
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
            return status[3]'''

    def kick_off(self):
        return self.ko_date.strftime('%H:%M')

    def matchday(self):
        return self.ko_date.strftime('%d %b %Y')

    def get_scoreline(self, force_update=False):
        api_url = "https://www.thesportsdb.com/api/v1/json/1/lookupevent.php?id=" + str(self.api_id)
        try:
            ko_date = datetime.now(self.ko_date)
        except:
            ko_date = self.ko_date
        match_status = self.status != "Match Finished" and \
                       self.status != "Match Postponed" and \
                       ko_date < datetime.now(pytz.utc)

        if (match_status and self.last_api < (datetime.now(pytz.utc) - timedelta(minutes=15))) or force_update:
            r = requests.get(api_url)
            self.last_api = datetime.now()
            self.save()
            if r:
                result_dict = r.json()['events'][0]
                home_score = result_dict['intHomeScore']
                away_score = result_dict['intAwayScore']
                postponed = result_dict['strPostponed']
                status = result_dict['strStatus']
                if status == 'Match Postponed':
                    print("Match Postponed")
                    self.status = status
                    self.Postponed = postponed
                    self.save()
                elif status == 'Match Finished':
                    self.home_score = home_score
                    self.away_score = away_score
                    self.status = status
                    self.save()
                    return str(home_score) + "-" + str(away_score)
                else:
                    print("Match hasn't finished")
                    return None
            else:
                print("No API Data retrieved")
                return None
        else:
            print("Too soon to call API or no need to call")
            return None
