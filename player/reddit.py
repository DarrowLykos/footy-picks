#! python3
import praw
import pandas as pd
import datetime as dt
from praw.models import MoreComments
from django.utils import timezone
import datetime
from player.models import Player, User
from bs4 import BeautifulSoup
from gameweek.models import Game, Prediction
from team.models import Team, Match, Competition


def get_reddit_predictions(comments_id, game_id):
    reddit = praw.Reddit(client_id='BxTTVEDgg6Ah9Q', \
                         client_secret='ntLunPI9lmYb_v0gQEZEfKI5fMs', \
                         user_agent='fpl predictions')
    # username='footypicks', \
    # password='xdudbaar187')

    submission = reddit.submission(id=comments_id)
    submission.comments.replace_more(limit=None)

    for comment in submission.comments.list():
        author = str(comment.author.name)
        comm = comment.body_html
        time = datetime.datetime.fromtimestamp(comment.created_utc)
        edited = comment.edited

        # print(f"{author}: {comm} ({time}, {edited})")

        fp_player = Player.objects.filter(user__username=author)

        if fp_player.count():
            fp_player = Player.objects.get(user__username=author)
            print(fp_player)
        else:
            new_player = User.objects.create(username=author)
            Player.objects.create(user=new_player)
            fp_player = Player.objects.get(user__username=author)
            print("new player created: " + author)

        soup = BeautifulSoup(comm, 'html.parser')
        html_tag = "li"
        unordered_list = soup.find_all("li")
        if not unordered_list:
            html_tag = "p"
            unordered_list = soup.find_all("p")

        if author == "farcough187":
            print(soup)
            print(unordered_list)
            print(comm)

        for fixture in unordered_list:
            try:
                if not fixture.string[0].isalnum():
                    fstring = fixture.string[1:]
                else:
                    fstring = fixture.string
                print(fstring)

                teams = fstring[0:-6]
                score = fstring[-5:][1:-1].split("-")
            except TypeError as err:
                for s in fixture.strings:
                    if s != None:
                        teams = s[0:-6]
                        score = s[-5:][1:-1].split("-")

            teams = teams.split(" v ")

            try:
                home_team = teams[0].strip(" \u2060")
                away_team = teams[1].strip(" \u2060")
                home_team = Team.objects.filter(name=home_team)[0]
                away_team = Team.objects.filter(name=away_team)[0]
                home_score = score[0]
                away_score = score[1]
            except IndexError as err:
                print("Not a prediction. Prob a general comment")
                continue

            comp = Competition.objects.get(api_id=4328)
            match = Match.objects.filter(home_team=home_team, away_team=away_team, competition=comp)[0]
            game = Game.objects.get(pk=game_id)

            if home_score.isnumeric() and away_score.isnumeric():
                latest = Prediction.objects.filter(match=match, player=fp_player, game=game, replaced=False)
                prediction = Prediction.objects.create(match=match, player=fp_player, home_score=home_score,
                                                       away_score=away_score, game=game)

                if author == "farcough187":
                    print(latest)
                    print(latest.count())
                if latest.count() > 1:
                    if latest[0].predicted_score() != prediction.predicted_score():
                        print("Prediction has changed")
                        latest[0].replaced = True
                        latest[0].save()
                        prediction.save()
                    else:
                        print("Prediction already exists")
                        prediction.delete()

                else:
                    print("Prediction saved")
                    prediction.save()

        # TODO: check comments match format
        # TODO: check date of comment
        # TODO: loop comment and extract prediction
        # TODO: get matching fixture from team.matches
        # TODO: create prediction and edit the datestamp to match time
