from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Match, Competition, Team


# Register your models here.
def get_image(obj):
    return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
        url=obj.thumbnail.url,
        width=obj.headshot.width,
        height=obj.headshot.height,
    )
    )


class MatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'ko_date', 'final_score')
    list_filter = ['ko_date']
    fieldsets = [
        (None, {'fields': ['status']}),
        ('Teams', {'fields': (('home_team', 'away_team', 'competition'),)}),
        ('Score', {'fields': (('home_score', 'away_score', 'result'),)}),
        ('Kick Off', {'fields': (['ko_date'])}),
        ('Other Information', {'fields': (('extra_time', 'penalties', 'postponed'),)})
    ]
    readonly_fields = ['status']


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'comp_type')
    readonly_fields = ["thumbnail_image"]
    fieldsets = [
        (None, {'fields': (('name',), 'thumbnail', 'thumbnail_image',)}),
        ('Information', {'fields': (('country', 'comp_type'),)}),
    ]

    def thumbnail_image(self, obj):
        return get_image(obj)

    thumbnail_image.short_description = (" ")


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ['country']
    readonly_fields = ['thumbnail_image']
    fieldsets = [
        (None, {'fields': (('name', 'short_name'),)}),
        ('Logo', {'fields': ('thumbnail', 'thumbnail_image')}),
        ('Competition', {'fields': (('country', 'competitions'),)}),
    ]

    def thumbnail_image(self, obj):
        return get_image(obj)

    thumbnail_image.short_description = (" ")


admin.site.register(Match, MatchAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Competition, CompetitionAdmin)
