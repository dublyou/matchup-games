from django.contrib import admin
from .models import League, LeagueMember, Team, LeagueDivision

admin.site.register(League)
admin.site.register(Team)
admin.site.register(LeagueMember)
admin.site.register(LeagueDivision)