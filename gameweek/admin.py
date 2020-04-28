from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Match, League, Competition, Game, Prediction, Team
#from rule.models import Rule

def get_image(obj):
    return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
        url=obj.thumbnail.url,
        width=obj.headshot.width,
        height=obj.headshot.height,
    )
    )

class MatchesInline(admin.TabularInline):
    verbose_name = "Match"
    verbose_name_plural = "Included Matches"
    model = Game.matches.through
    extra = 4

# class GamesInline(admin.TabularInline):
#     verbose_name = "Sub-Game"
#     verbose_name_plural = "Sub-Games"
#     model = Game.aggregated_games.through
#     extra = 0

#class RulesInline(admin.StackedInline):
#    model = Game.rules.through

class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'total_matches')
    list_filter = ['start_date', 'end_date']
    fieldsets = [
            (None,               {'fields': (('name', 'status'), ('available', 'public_game'))}),
            ('Date Information', {'fields': (('start_date', 'end_date'),)}),
            ('Money Information', {'fields': (('entry_fee', 'prize_pool'),)}),
            ('Owner Information', {'fields': ('created_by',)}),
            ('Rules Information', {'fields': ['rules']}),
            ('Matches Information', {'fields': (('total_matches', 'completed_matches', 'in_play_matches',
                                                   'to_play_matches',),)}),
            #('Leagues Information', {'fields': ['leagues_included_in']}),
        ]
    inlines = [MatchesInline]
    readonly_fields = ['prize_pool', 'status', 'total_matches', 'completed_matches', 'in_play_matches',
                       'to_play_matches']
    
    # def total_matches(self, obj):
    #    return obj.matches.all().count()
        
class MatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'ko_date',  'final_score')
    list_filter = ['ko_date']
    fieldsets = [
            (None, {'fields': ['status']}),
            ('Teams',               {'fields': (('home_team','away_team', 'competition'),)}),
            ('Score', {'fields': (('home_score', 'away_score', 'result'),)}),
            ('Kick Off', {'fields': (['ko_date'])}),
            ('Other Information', {'fields': (('extra_time', 'penalties', 'postponed'),)})
        ]   
    readonly_fields = ['status']

#class MatchProxyAdmin(admin.ModelAdmin):
#    fieldsets = [
#            ('Teams',               {'fields': (('home_team','away_team', 'competition'),)}),
#            ('Kick Off', {'fields': (['ko_date'])}),
#            ('Other Information', {'fields': (('extra_time', 'penalties'),)})
#        ]  
    
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'comp_type')
    readonly_fields = ["thumbnail_image"]
    fieldsets = [
        (None, {'fields': (('name', ), 'thumbnail', 'thumbnail_image', ) }),
        ('Information', {'fields': (('country', 'comp_type'), )}),
    ]

    def thumbnail_image(self, obj):
        return get_image(obj)
    thumbnail_image.short_description = (" ")

class PredictionAdmin(admin.ModelAdmin):
    list_display = ['player', "match", "valid", ]
    readonly_fields = ['valid', 'points', 'actual_score', 'predicted_score', ]
    list_filter = ['player']
    fieldsets = [
            (None,                  {'fields': (('player', 'valid'),)}),
            ('Prediction',          {'fields': (('match', 'game'), ('home_score', 'away_score', "joker"), )}),
            ('Scoring',             {'fields': (('actual_score', 'predicted_score'), 'points'), } )
        ]
    #TODO: add inline of read only rules
    
    def get_player(self, obj):
        return obj.user.username
    get_player.admin_order_field  = 'player'  #Allows column order sorting
    get_player.short_description = 'Player'  #Renames column head

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ['country']
    readonly_fields = ['thumbnail_image']
    fieldsets = [
        (None,              {'fields': (('name', 'short_name'),)}),
        ('Logo',            {'fields': ('thumbnail', 'thumbnail_image')}),
        ('Competition',     {'fields': (('country', 'competitions'),)}),
    ]

    def thumbnail_image(self, obj):
        return get_image(obj)
    thumbnail_image.short_description = (" ")

class LeagueMembersInline(admin.StackedInline):
    verbose_name = "Member"
    verbose_name_plural = "Members"
    model = League.members.through
    extra = 0

class LeagueGamesInline(admin.StackedInline):
    verbose_name = "Game"
    verbose_name_plural = "Games"
    model = League.games.through
    extra = 0

class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_private', 'owned_by')
    list_filter = ['owned_by', 'is_private']
    fieldsets = [
        (None, {'fields': ('name', )}),
        ('League Information', {'fields': (('owned_by', 'pword'), ('is_private', 'member_can_add',) )}),
    ]
    inlines = [LeagueMembersInline, LeagueGamesInline]

admin.site.register(Match, MatchAdmin)
admin.site.register(League, LeagueAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Prediction, PredictionAdmin)
admin.site.register(Team, TeamAdmin)