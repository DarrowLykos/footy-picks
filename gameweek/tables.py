import django_tables2 as tables
from .models import Prediction


class LeaderboardTable(tables.Table):
    class Meta:
        model = Prediction
