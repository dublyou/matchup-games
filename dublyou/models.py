from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

EVENT_TYPES = (
    (1, "series"),
    (2, "tournament"),
    (3, "season"),
    (4, "olympics")
)

COMP_TYPES = (
    (1, "individual"),
    (2, "team"),
    (3, "league")
)

SPLIT_TEAMS = (
    (1, "random"),
    (2, "manual")
)

TOURNEY_TYPES = (
    (1, "single elimination"),
    (2, "double elimination")
)

TOURNEY_SEEDS = (
    (1, "random"),
    (2, "assigned")
)

SEASON_METHODS = (
    (1, "round robin"),
    (2, "input")
)

PLAYOFF_FORMATS = (
    (1, "single elimination"),
    (2, "double elimination"),
    (3, "series best of")
)

STATES = (
    ("AL", "Alabama"),
    ("AK", "Alaska"),
    ("AZ", "Arizona"),
    ("AR", "Arkansas"),
    ("CA", "California"),
    ("CO", "Colorado"),
    ("CT", "Connecticut"),
    ("DE", "Delaware"),
    ("DC", "Dist of Columbia"),
    ("FL", "Florida"),
    ("GA", "Georgia"),
    ("HI", "Hawaii"),
    ("ID", "Idaho"),
    ("IL", "Illinois"),
    ("IN", "Indiana"),
    ("IA", "Iowa"),
    ("KS", "Kansas"),
    ("KY", "Kentucky"),
    ("LA", "Louisiana"),
    ("ME", "Maine"),
    ("MD", "Maryland"),
    ("MA", "Massachusetts"),
    ("MI", "Michigan"),
    ("MN", "Minnesota"),
    ("MS", "Mississippi"),
    ("MO", "Missouri"),
    ("MT", "Montana"),
    ("NE", "Nebraska"),
    ("NV", "Nevada"),
    ("NH", "New Hampshire"),
    ("NJ", "New Jersey"),
    ("NM", "New Mexico"),
    ("NY", "New York"),
    ("NC", "North Carolina"),
    ("ND", "North Dakota"),
    ("OH", "Ohio"),
    ("OK", "Oklahoma"),
    ("OR", "Oregon"),
    ("PA", "Pennsylvania"),
    ("RI", "Rhode Island"),
    ("SC", "South Carolina"),
    ("SD", "South Dakota"),
    ("TN", "Tennessee"),
    ("TX", "Texas"),
    ("UT", "Utah"),
    ("VT", "Vermont"),
    ("VA", "Virginia"),
    ("WA", "Washington"),
    ("WV", "West Virginia"),
    ("WI", "Wisconsin"),
    ("WY", "Wyoming"),
)


class Profile(models.Model):
    # Relations
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        verbose_name=_("user")
    )

    active = models.BooleanField(default=False)
    mobile_number = models.IntegerField()
    zip_code = models.IntegerField()
    creation_datetime = models.DateTimeField(auto_now_add=True)

    # Custom Properties
    @property
    def username(self):
        return self.user.username

    # Methods

    # Meta and String
    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ("user",)

    def __str__(self):
        return self.user.username


class GameEvent(models.Model):
    event_name = models.CharField(max_length=50, null=True, blank=True)
    event_type = models.IntegerField(choices=EVENT_TYPES)
    game_type = models.ForeignKey(GameType, null=True)
    comp_type = models.IntegerField(choices=COMP_TYPES)
    num_children = models.IntegerField()
    parent_event = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    child_num = models.IntegerField(null=True)
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE)
    creation_datetime = models.DateTimeField(auto_now_add=True)


class EventCompetitors(models.Model):
    event = models.ForeignKey(GameEvent, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ("event", "user", "team", "league")


class Game(models.Model):
    game_type = models.ForeignKey(GameType)
    game_date = models.DateTimeField(null=True, blank=True)
    game_venue = models.ForeignKey(GameVenue, null=True)
    parent_event = models.ForeignKey(GameEvent, null=True, blank=True)
    child_num = models.IntegerField(null=True)
    competitors = models.ManyToManyField(User, through='Matchup', null=True)
    teams = models.ManyToManyField(Team, through='TeamMatchup', null=True)
    witness = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_datetime = models.DateTimeField(auto_now_add=True)


class Matchup(models.Model):
    game = models.ForeignKey(Game)
    user = models.ForeignKey(Profile)
    game_on = models.BooleanField(default=False)
    place = models.IntegerField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    seed = models.IntegerField()

    class Meta:
        unique_together = ("game", "user")


class TeamMatchup(models.Model):
    game = models.ForeignKey(Game)
    team = models.ForeignKey(Team)
    game_on = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    round = models.IntegerField(default=1)
    place = models.IntegerField(null=True)
    score = models.IntegerField(null=True)
    seed = models.IntegerField()

    class Meta:
        unique_together = ("game", "team")


class Team(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=50)
    captain = models.ForeignKey(Profile, on_delete=models.CASCADE)
    team_members = models.ManyToManyField(Profile, through='TeamMember')
    max_members = models.IntegerField(null=True)
    division = models.ForeignKey(LeagueDivision, null=True)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("league", "team_name")


class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    member = models.ForeignKey(Profile, on_delete=models.CASCADE)
    admin = models.BooleanField(default=False)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("team", "member")


class SubTeam(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    member = models.ForeignKey(TeamMember, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("game", "member")


class League(models.Model):
    league_name = models.CharField(max_length=50)
    comp_type = models.IntegerField(choices=COMP_TYPES)
    league_members = models.ManyToManyField(Profile, through='LeagueMember')
    game_type = models.ForeignKey(GameType, null=True)
    commissioner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    base_city = models.CharField(max_length=20)
    max_members = models.IntegerField(null=True, blank=True)
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE)
    creation_datetime = models.DateTimeField(auto_now_add=True)


class LeagueMember(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    member = models.ForeignKey(Profile, on_delete=models.CASCADE)
    division = models.ForeignKey(LeagueDivision)
    admin = models.BooleanField(default=False)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("league", "member")


class LeagueDivision(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    division_name = models.CharField(max_length=25)


class GameType(models.Model):
    game_name = models.CharField(max_length=25)
    game_rules = models.TextField(max_length=500)
    comp_type = models.IntegerField(choices=COMP_TYPES)
    comp_per_team = models.IntegerField(null=True, blank=True)
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE)
    creation_datetime = models.DateTimeField(auto_now_add=True)


class GameVenue(models.Model):
    venue_name = models.CharField(max_length=50)
    street_address = models.CharField(max_length=50)
    city = models.CharField(max_length=20)
    state = models.CharField(choices=STATES)
    zip_code = models.CharField(max_length=5)
    game_type = models.ManyToManyField(GameType)
    venue_type = models.IntegerField(choices=((1, "private"), (2, "public")))
