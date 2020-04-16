from django.contrib import admin

from .models import Match, MatchProxy, Competition, Game, Prediction, Team
#from rule.models import Rule
    
class MatchesInline(admin.TabularInline):
    verbose_name = "Match"
    verbose_name_plural = "Included Matches"
    model = Game.matches.through
    extra = 4
    
#class RulesInline(admin.StackedInline):
#    model = Game.rules.through

class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    list_filter = ['start_date', 'end_date']
    fieldsets = [
            (None,               {'fields': ['name']}),
            ('Date Information', {'fields': (['start_date', 'end_date'])}),
            ('Money Information', {'fields': (('entry_fee', 'prize_pool'),)}),
            ('Other Information', {'fields': ['available','rules']})
        ]
    inlines = [MatchesInline]
    
class MatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'ko_datetime',  'final_score')
    list_filter = ['ko_datetime']
    fieldsets = [
            (None, {'fields': ['status']}),
            ('Teams',               {'fields': (('home_team','away_team', 'competition'),)}),
            ('Score', {'fields': (('home_score', 'away_score', 'result'),)}),
            ('Kick Off', {'fields': (['ko_datetime'])}),
            ('Other Information', {'fields': (('extra_time', 'penalties', 'postponed'),)})
        ]   
    readonly_fields = ['status']

#class MatchProxyAdmin(admin.ModelAdmin):
#    fieldsets = [
#            ('Teams',               {'fields': (('home_team','away_team', 'competition'),)}),
#            ('Kick Off', {'fields': (['ko_datetime'])}),
#            ('Other Information', {'fields': (('extra_time', 'penalties'),)})
#        ]  
    
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'comp_type')

class PredictionAdmin(admin.ModelAdmin):
    #list_display = ['player', "match", "valid", ]
    readonly_fields = ['valid']
    #list_filter = ['player']
    
#    def get_player(self, obj):
#        return obj.user.username
#    get_player.admin_order_field  = 'player'  #Allows column order sorting
#    get_player.short_description = 'Player'  #Renames column head
    
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ['country']
    #readonly_fields = ['thumbnail_image']
    
#    def thumbnail_image(self, obj):
#        to_return = '<img src="{url}" width="{width}" height={height} />'.format(
#            url = obj.thumbnail.url,
#            width=obj.thumbnail.width,
#            height=obj.thumbnail.height,
#            )
#        return {{ to_return }}
    
admin.site.register(Match, MatchAdmin)
#admin.site.register(MatchProxy, MatchProxyAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Prediction, PredictionAdmin)
admin.site.register(Team, TeamAdmin)