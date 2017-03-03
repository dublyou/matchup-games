from django.contrib import admin
from .models import League, LeaguePlayer, Team, LeagueDivision, LeagueInvite, LeagueSignUpPage

admin.site.register(League)
admin.site.register(Team)
admin.site.register(LeaguePlayer)
admin.site.register(LeagueDivision)
admin.site.register(LeagueInvite)
admin.site.register(LeagueSignUpPage)