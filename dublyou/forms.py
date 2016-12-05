from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
# from django.utils.translation import ugettext_lazy as _
from .constants import DEFAULT_INPUT_CLASSES, INPUT_HTML_OUTPUT
import re


class FormTree(object):
    def __init__(self, *args, **kwargs):
        pass


class MyBaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(MyBaseForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            field.widget.attrs.update({
                'class': DEFAULT_INPUT_CLASSES
            })

    def as_input_group(self):
        return self._html_output(
            normal_row=INPUT_HTML_OUTPUT,
            error_row='<li>%s</li>',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=False)

    def clean_dependent_inputs(self, input_tree, input_criteria):
        valid = True
        cleaned_data = self.cleaned_data
        dep_inputs = input_tree["fields"][cleaned_data[input_tree["name"]]]
        for dep_input in dep_inputs:
            input_name = dep_input["name"] if type(dep_input) is dict else dep_input
            input_value = cleaned_data[input_name]
            criteria = input_criteria[input_name]
            if criteria is str:
                if not re.match(criteria, input_value):
                    self.add_error(input_name, forms.ValidationError(message="Invalid input", code="invalid"))
                    valid = False
            elif input_value not in criteria:
                self.add_error(input_name, forms.ValidationError(message="Invalid input", code="invalid"))
                valid = True
            if type(dep_input) is dict:
                if "fields" in dep_input.keys() and valid:
                    self.clean_dependent_inputs(input_tree=dep_input, input_criteria=input_criteria)
        return valid


class MyBaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MyBaseModelForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            field.widget.attrs.update({
                'class': DEFAULT_INPUT_CLASSES
            })

    def as_input_group(self):
        return self._html_output(
            normal_row=INPUT_HTML_OUTPUT,
            error_row='<li>%s</li>',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=False)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=True, max_length=50)
    first_name = forms.CharField(label="First Name", required=True, max_length=30)
    last_name = forms.CharField(label="Last Name", required=True, max_length=30)

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': DEFAULT_INPUT_CLASSES,
                'placeholder': field.label
            })

    class Meta:
        model = User
        fields = ("email", "password1", "password2", "first_name", "last_name")

    def as_input_group(self):
        return self._html_output(
            normal_row=INPUT_HTML_OUTPUT,
            error_row='<li>%s</li>',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=False)

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)

        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()

        return user
