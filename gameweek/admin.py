from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import League, Game, Prediction
#from rule.models import Rule

class MatchesInline(admin.TabularInline):
    verbose_name = "Match"
    verbose_name_plural = "Included Matches"
    model = Game.matches.through
    extra = 4

class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'total_matches')
    list_filter = ['start_date', 'end_date']
    fieldsets = [
            (None,               {'fields': (('name', 'status'), ('available', 'public_game'))}),
            ('Date Information', {'fields': (('start_date', 'end_date'),)}),
            ('Money Information', {'fields': (('entry_fee', 'prize_pool'),)}),
            ('Owner Information', {'fields': (('created_by','owned_by'), )}),
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

class PredictionAdmin(admin.ModelAdmin):
    list_display = ['player', "match", "valid", 'points']
    readonly_fields = ['valid', 'points', 'actual_score', 'predicted_score', ]
    list_filter = ['player', 'match', 'game']
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
        ('League Information', {'fields': (('owned_by', 'pword'), ('is_private', 'member_can_add','accepts_members'))}),
    ]
    inlines = [LeagueMembersInline, LeagueGamesInline]


admin.site.register(League, LeagueAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Prediction, PredictionAdmin)
