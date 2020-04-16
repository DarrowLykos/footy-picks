from django.contrib import admin
from django import forms
# Register your models here.
from .models import Rule, Payout, RulePayout

#class PrizesInline(admin.StackedInline):
#    verbose_name = "Prize"
#    verbose_name_plural = "Prizes"
#    model = Payout.payouts.through
#    extra = 3

class PayoutAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'split_if_tied')
    fieldsets = [
            (None,               {'fields': (( 'split_if_tied'),)}),
            ("Payouts", {'fields': (('position', 'percentage'),)}),
        ]
    
class PayoutInlineForm(forms.ModelForm):
    title = forms.CharField(max_length=128)
 
    class Meta:
        model = Payout
        fields = ('title', )  
        
class PayoutsInline(admin.TabularInline):
    verbose_name = "Payout"
    verbose_name_plural = "Payouts"
    model = Rule.payouts.through
    #model= RulePayout
    extra = 0
    
class RuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'correct_score', 'correct_result', 'correct_home_score',
                    'correct_away_score', 'joker_count', 'joker_multiplier_x', 'get_payouts')
    fieldsets = [
            (None, {'fields': (('name', ('correct_score', 'correct_result'),
                                    ('correct_home_score', 'correct_away_score'), 
                                    ('joker_count', 'joker_multiplier') ))}),
        ]
    inlines = [PayoutsInline]
    
    def joker_multiplier_x(self, obj):
        return "X" + str(obj.joker_multiplier)
    
    def get_payouts(self, obj):
        obj_ordered = obj.payouts.order_by('position')
        return "\n, ".join([str(p) for p in obj_ordered.all()])
    get_payouts.short_description = "Payouts"
    
admin.site.register(Rule, RuleAdmin)
##admin.site.register(Prize)
admin.site.register(Payout, PayoutAdmin)