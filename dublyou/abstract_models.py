from django.db import models
from django.shortcuts import reverse
from django.core.validators import RegexValidator

from invitations.models import Invitation

NAME_REGEX = r"^[-\s\.\w\d]{1,30}$"


class BaseProfileModel(models.Model):
    STATUS_TYPES = ((0, "inactive"), (1, "active"))
    name = models.CharField(max_length=30, validators=[RegexValidator(NAME_REGEX)])
    abbrev = models.CharField(max_length=4, null=True, blank=True)
    status = models.IntegerField(choices=STATUS_TYPES, default=0)

    def get_absolute_url(self):
        return reverse(type(self).__name__.lower(), kwargs={"pk": self.id})

    def __str__(self):
        return self.name + (" ({})".format(self.abbrev) if self.abbrev else "")

    class Meta:
        abstract = True


class BaseInviteModel(models.Model):
    INVITE_TYPES = ((1, "regular"), (2, "open"))
    create_fields = []
    delete_field = []

    invite = models.ForeignKey(Invitation, null=True, blank=True, related_name="pending_invites")
    expiration = models.DateTimeField(null=True, blank=True)
    invite_type = models.IntegerField(choices=INVITE_TYPES, default=1)
    approved = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)

    # Methods
    def get_absolute_url(self):
        return reverse(self.INVITE_MODEL.__name__.lower(), kwargs={"pk": self.invite_instance.id}) + "invite/{}/".format(self.pk)

    def approve(self):
        if self.accepted:
            self.INVITE_MODEL.create(**{field: getattr(self, field) for field in self.create_fields})
            self.__class__.objects.filter(**{field: getattr(self, field) for field in self.delete_fields}).delete()
        else:
            self.approved = True
            self.save()

    def accept(self):
        self.INVITE_MODEL.create(**{field: getattr(self, field) for field in self.create_fields})
        self.__class__.objects.filter(**{field: getattr(self, field) for field in self.delete_fields}).delete()

    def __str__(self):
        return self.profile or self.invite.email

    class Meta:
        abstract = True
