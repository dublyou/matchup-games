from django import forms

from .models import Profile
from ...forms import MyBaseModelForm
from .fields import HeightField


class EditProfileForm(MyBaseModelForm):
    height = HeightField(required=True)

    class Meta:
        model = Profile
        fields = ['abbrev', 'mobile_number', 'birth_date', 'height', 'weight', 'gender',
                  'current_zip', 'hometown_zip', 'user_image', 'privacy_type']

    def clean(self):
        cleaned_data = super(EditProfileForm, self).clean()
        profiles = Profile.objects.filter(abbrev=cleaned_data['abbrev']).exclude(id=self.instance.id)
        if profiles.exists():
            raise forms.ValidationError(
                'abbrev is taken.',
                code='duplicate'
            )
        return cleaned_data

