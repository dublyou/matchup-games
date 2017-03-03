from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.validators import RegexValidator

from invitations.models import Invitation
from smart_selects.db_fields import ChainedForeignKey

from ...constants import MATCHUP_TYPES
from ..games.models import Game
from ..profile.models import Profile
from ...utils import upload_to_path, send_notification
# from django.core.validators import RegexValidator, EmailValidator
# from django.utils.translation import ugettext_lazy as _

NAME_REGEX = r"^[-\s\.\w\d]{1,30}$"


class League(models.Model):
    LEAGUE_STATUS = (
        (1, "active"),
        (2, "inactive")
    )
    name = models.CharField(max_length=30, validators=[RegexValidator(NAME_REGEX)])
    abbrev = models.CharField(max_length=4, null=True, blank=True)
    matchup_type = models.IntegerField(choices=MATCHUP_TYPES, default=1)
    players = models.ManyToManyField(Profile, through='LeaguePlayer', related_name="league_set")
    invitees = models.ManyToManyField(Profile, through='LeagueInvite', related_name="invited_leagues")
    games = models.ManyToManyField(Game, blank=True)
    commissioner = models.ForeignKey(Profile, related_name='comm_leagues')
    base_city = models.CharField(max_length=20, null=True, blank=True)
    max_members = models.IntegerField(null=True, blank=True)
    league_emblem = models.FileField(upload_to=upload_to_path, null=True, blank=True)
    league_bg = models.FileField(upload_to="dublyou/static/img/league/bg", null=True, blank=True)
    status = models.IntegerField(choices=LEAGUE_STATUS, default=1)
    privacy_type = models.IntegerField(choices=((1, "private"), (2, "public")), default=1)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    @property
    def profile_image(self):
        if self.league_emblem:
            return self.league_emblem.url
        return "/static/svg/profile_league.png"

    # Methods
    def get_absolute_url(self):
        return reverse('league', kwargs={"pk": self.id})

    class Meta:
        unique_together = (("name", "status"), ("abbrev", "status"))

    def __str__(self):
        return self.name + (" ({})".format(self.abbrev) if self.abbrev else "")


class LeagueDivision(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="divisions")
    division_name = models.CharField(max_length=30)

    class Meta:
        unique_together = ("league", "division_name")

    def __str__(self):
        return self.division_name


class Team(models.Model):
    TEAM_STATUS = (
        (1, "pending"),
        (2, "active"),
        (3, "inactive")
    )
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="teams")
    name = models.CharField(max_length=30, validators=[RegexValidator(NAME_REGEX)])
    abbrev = models.CharField(max_length=4, null=True, blank=True)
    captain = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="team_captain",
                                null=True, blank=True)
    max_members = models.IntegerField(default=10)
    division = ChainedForeignKey(
        LeagueDivision,
        chained_field="league",
        chained_model_field="league",
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
        blank=True
    )
    status = models.IntegerField(choices=TEAM_STATUS, default=1)
    team_logo = models.FileField(upload_to=upload_to_path, null=True)
    team_bg = models.FileField(upload_to="dublyou/static/img/team/bg", null=True)

    players = models.ManyToManyField(Profile, through='LeaguePlayer', through_fields=('team', 'player'),
                                     related_name="teams")

    @property
    def league_members(self):
        return self.league.league_members

    @property
    def profile_image(self):
        if self.team_logo:
            return self.team_logo.url
        return "/static/svg/profile_team.png"

    # Methods
    def get_absolute_url(self):
        return reverse('team', kwargs={"pk": self.id})

    class Meta:
        unique_together = (("league", "name"), ("league", "abbrev"))

    def __str__(self):
        return self.name + (" ({})".format(self.abbrev) if self.abbrev else "")


class LeagueSignUpPage(models.Model):
    league = models.OneToOneField(League, on_delete=models.CASCADE, related_name="signup_page")
    verification_key = models.CharField(max_length=40, primary_key=True)
    expiration = models.DateTimeField(null=True, blank=True)
    msg_image = models.ImageField(upload_to=upload_to_path, null=True, blank=True)

    @property
    def commissioner(self):
        return self.league.commissioner

    @property
    def image(self):
        if self.msg_image:
            return self.msg_image.url
        return "/static/svg/profile_league.png"

    # Methods
    def get_absolute_url(self):
        return reverse('league_signup', kwargs={"pk": self.league.id, "key": self.pk})

    def key_expired(self):
        if self.expiration:
            return self.expiration <= timezone.now()
        return False


class LeagueInvite(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="invites")
    player = models.ForeignKey(Profile, null=True, blank=True, related_name="league_invites")
    team = ChainedForeignKey(
        Team,
        chained_field="league",
        chained_model_field="league",
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
        blank=True,
        related_name="team_invites"
    )
    division = ChainedForeignKey(
        LeagueDivision,
        chained_field="league",
        chained_model_field="league",
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
        blank=True
    )
    invite = models.ForeignKey(Invitation, null=True, blank=True, related_name="pending_players")
    expiration = models.DateTimeField(null=True, blank=True)
    invite_type = models.IntegerField(choices=((1, "league"), (2, "team"), (3, "open")), default=1)
    approved = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)

    # Methods
    def get_absolute_url(self):
        return reverse('league', kwargs={"pk": self.league.id}) + "invite/{}/".format(self.pk)

    def approve(self):
        if self.accepted:
            LeaguePlayer.create(league=self.league, player=self.player, team=self.team)
            LeagueInvite.objects.filter(league=self.league, player=self.player).delete()
        else:
            self.approved = True
            self.save()

    def accept(self):
        LeaguePlayer.create(league=self.league, member=self.player)
        LeagueInvite.objects.filter(league=self.league, player=self.player).delete()

    class Meta:
        unique_together = ("league", "player", "team")

    def __str__(self):
        return self.player or self.invite.email


class LeaguePlayer(models.Model):
    MEMBER_STATUS = (
        (1, "active"),
        (2, "inactive")
    )
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="league_players")
    player = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    team = ChainedForeignKey(
        Team,
        chained_field="league",
        chained_model_field="league",
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
        blank=True
    )
    division = ChainedForeignKey(
        LeagueDivision,
        chained_field="league",
        chained_model_field="league",
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
        blank=True
    )
    balance = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True)
    admin = models.BooleanField(default=False)
    status = models.IntegerField(choices=MEMBER_STATUS, default=1)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("league", "player")


from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=LeagueInvite)
def send_league_invite(sender, created, instance, **kwargs):
    profile = instance.player
    if created and profile:
        params = {
            "user": profile.user,
            "subject": "You're Invited!",
            "template": "emails/invitation.html",
            "object_type": "competition",
            "instance": instance.team or instance.league
        }
        send_notification(**params)
