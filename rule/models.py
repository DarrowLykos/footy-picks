from django.db import models

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

#class Prize(models.Model):
#    
#    def valid_pct(value):
#        if value.endswith("%"):
#           return float(value[:-1])/100
#        else:
#           try:
#              return float(value)
#           except ValueError:          
#              raise ValidationError(
#                  _('%(value)s is not a valid pct'),
#                    params={'value': value},
#               )
#              
#    position = models.IntegerField()
#    percentage = models.DecimalField(max_digits=10, decimal_places=4, validators=[valid_pct])
#    
#    def __str__(self):
#        return str(self.position) + suffix(self.position) + " place: " + str(self.percentage * 100) + "%"
           
class Payout(models.Model):
    
    def valid_pct(value):
        if value.endswith("%"):
           return float(value[:-1])/100
        else:
           try:
              return float(value)
           except ValueError:          
              raise ValidationError(
                  _('%(value)s is not a valid pct'),
                    params={'value': value},
               )
              
    #name = models.CharField(max_length=100, null=True, blank=True)
    position = models.IntegerField(default=1)
    percentage = models.DecimalField(default=1, max_digits=10, decimal_places=4)

    #payouts = models.ManyToManyField(Prize)
    split_if_tied = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.position) + suffix(self.position) + " place: " + str(self.percentage * 100) + "%"
    
# Create your models here.
class Rule(models.Model):
    name = models.CharField(max_length=100)
    correct_score = models.IntegerField(default=0)
    correct_result = models.IntegerField(default=0)
    correct_home_score = models.IntegerField(default=0)
    correct_away_score = models.IntegerField(default=0)
    joker_count = models.IntegerField(default=0)
    joker_multiplier = models.IntegerField(default=0)
    payouts = models.ManyToManyField(Payout, related_name="payouts")
    outpays = models.ManyToManyField(Payout, related_name="outpays", through='RulePayout')
    
    def __str__(self):
        return self.name   
    
    def get_payouts(self):
        return self.payouts.order_by('position')    
    
class RulePayout(models.Model):
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE)
    payout = models.ForeignKey(Payout, on_delete=models.CASCADE)