from django.db import models
from django.conf import settings
# from django.core.validators import RegexValidator, EmailValidator
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator


class Profile(models.Model):
    # Relations
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        verbose_name=_("user")
    )

    abbrev = models.CharField(max_length=6, unique=True)
    phone_regex = RegexValidator(regex=r'^\d{10}$',
                                 message="Phone number must be entered in the format: '999999999'. Up to 10 digits allowed.")
    mobile_number = models.CharField(max_length=10, unique=True, validators=[phone_regex])
    zip_code = models.CharField(max_length=5)
    user_image = models.FileField(upload_to="dublyou/static/img/profile/user", null=True)
    bg_image = models.FileField(upload_to="dublyou/static/img/profile/bg", null=True)
    rating = models.DecimalField(default=0, decimal_places=4, max_digits=5)
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
