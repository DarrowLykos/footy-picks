from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime

#Create your models here.
class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pic = models.ImageField(blank=True)

    # TODO: incorporate payments and winnings
    def __str__(self):  # __unicode__ for Python 2
        return self.user.username

    def name(self):
        return self.user.username

    def get_points_by_game(self, game_id):
        self.prediction_set.filter(game_id=game_id).aggregate(total_points=Sum('points'))

    def get_points_by_match(self, match_id):
        self.prediction_set.filter(match_id=match_id).aggregate(total_points=Sum('points'))


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("INC", "Income"),
        ("OUT", "Outgoing"),
        ("TRI", "Transfer in"),
        ("TRO", "Transfer out")
    )

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="transactions",
                               related_query_name="transaction")
    amount = models.DecimalField(decimal_places=2, max_digits=4)
    type = models.CharField(choices=TRANSACTION_TYPES, max_length=3)
    transfer_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="transfers",
                                        related_query_name="transfers", blank=True, null=True,
                                        verbose_name="Transferred from/to")
    date = models.DateField(default=now)
    pending = models.BooleanField(default=True)


"""
#@receiver(post_save, sender=User)
#def create_or_update_user_profile(sender, instance, created, **kwargs):
#    if created:
#        Player.objects.create(user=instance)
#    instance.profile.save()

#class Profile(models.Model):
#    user = models.OneToOneField(User, on_delete=models.CASCADE)
#    pic = models.ImageField(blank=True) 
#    
#@receiver(post_save, sender=User)
#def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        Profile.objects.create(user=instance)
#
#@receiver(post_save, sender=User)
#def save_user_profile(sender, instance, **kwargs):
#    instance.profile.save()
"""
