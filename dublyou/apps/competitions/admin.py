from django.contrib import admin
from . import models

admin.site.register(models.Competition)
admin.site.register(models.Competitor)
admin.site.register(models.CompetitionInvite)
admin.site.register(models.CompetitionSignUpPage)
admin.site.register(models.Matchup)
admin.site.register(models.MatchupCompetitor)
admin.site.register(models.Series)
admin.site.register(models.Tournament)
admin.site.register(models.TourneyRound)
admin.site.register(models.Season)
admin.site.register(models.Player)
admin.site.register(models.CompetitorSeed)
