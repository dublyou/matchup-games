from django import forms
from django.utils.translation import ugettext_lazy as _
from .constants import DEFAULT_INPUT_CLASSES, INPUT_HTML_OUTPUT
import re
import json
from allauth.account.forms import LoginForm, SignupForm as AllAuthSignUpForm


class CustomFormMixin(object):
    dependent_inputs = None
    error_css_class = "has-error"

    def custom_init(self):
        for name, field in self.fields.items():
            if not field.label:
                field.label = name.replace("_", " ").title()
            if hasattr(field, "empty_label"):
                field.empty_label = "Select {}".format(field.label)
            widget_class = field.widget.__class__.__name__
            widgets_not_allowed = ["CheckboxInput", "TimeWidget"]
            if widget_class not in widgets_not_allowed:
                field_classes = field.widget.attrs.get("class", "")
                field.widget.attrs.update({
                    'class': field_classes + " " + DEFAULT_INPUT_CLASSES,
                    'placeholder': field.label,
                    'title': field.label
                })
            widget_specific_classes = {
                "DateInput": " datepicker",
                "TimeInput": " timepicker"
            }
            if widget_class in widget_specific_classes:
                field_classes = field.widget.attrs.get("class", "")
                field.widget.attrs.update({
                    "class": field_classes + widget_specific_classes[widget_class],
                })

        if self.dependent_inputs:
            for input_tree in self.dependent_inputs:
                self.add_actions(input_tree)

    def as_input_group(self):
        return self._html_output(
            normal_row=INPUT_HTML_OUTPUT,
            error_row='<li>%s</li>',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=False)

    def as_mytable(self):
        return self._html_output(
            normal_row='<tr class="form-group %(css_classes)s"><th class="">%(label)s</th><td>%(errors)s%(field)s%(help_text)s</td></tr>',
            error_row='<tr><td colspan="2">%s</td></tr>',
            row_ender='</td></tr>',
            help_text_html='<br /><span class="helptext">%s</span>',
            errors_on_separate_row=False)

    def clean_dependent_inputs(self, input_tree, input_criteria):
        valid = True
        cleaned_data = self.cleaned_data
        dep_inputs = input_tree["fields"][cleaned_data[input_tree["name"]]]
        for dep_input in dep_inputs:
            input_name = dep_input["name"] if type(dep_input) is dict else dep_input
            input_value = cleaned_data.get(input_name, None)
            criteria = input_criteria.get(input_name, None)

            if criteria is not None:
                if criteria is str:
                    if not re.match(criteria, input_value):
                        self.add_error(input_name, forms.ValidationError(message="Invalid input", code="invalid"))
                        valid = False
                elif input_value not in criteria:
                    self.add_error(input_name, forms.ValidationError(message="Invalid input", code="invalid"))
                    valid = False
                if type(dep_input) is dict:
                    if "fields" in dep_input.keys() and valid:
                        self.clean_dependent_inputs(input_tree=dep_input, input_criteria=input_criteria)
            else:
                if not input_value:
                    valid = False
        return valid

    def add_actions(self, input_tree, actions={}):
        input_name = input_tree.get("name")
        if "fields" in input_tree:
            if input_name in self.fields:
                self.fields[input_name].widget.attrs.update({
                    'data-action-change': "toggle"
                })

            dependents = {}
            recurse = {}
            for value, ls in input_tree["fields"].items():
                for dependent_field in ls:
                    field_name = dependent_field["name"] if type(dependent_field) == dict else dependent_field

                    if field_name in dependents:
                        dependents[field_name].append(value)
                    else:
                        dependents[field_name] = [value]
                        if type(dependent_field) == dict:
                            recurse[field_name] = dependent_field

            for field_name, value in dependents.items():
                data_attrs = {}
                if input_name in self.fields:
                    data_trigger = json.loads(actions.get("data-trigger", "[]"))
                    data_trigger.append(input_name)
                    data_toggle = json.loads(actions.get("data-toggle", "{}"))
                    data_toggle[input_name] = value
                    data_attrs = {
                        "data-trigger": json.dumps(data_trigger),
                        "data-toggle": json.dumps(data_toggle),
                        "data-group": ".form-group"
                    }
                if field_name in recurse:
                    self.add_actions(recurse[field_name], data_attrs)
                if field_name in self.fields:
                    self.fields[field_name].widget.attrs.update(data_attrs)


class MyBaseForm(forms.Form, CustomFormMixin):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.user = self.request.user if self.request else None
        super(MyBaseForm, self).__init__(*args, **kwargs)
        self.custom_init()


class MyBaseModelForm(forms.ModelForm, CustomFormMixin):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.user = self.request.user if self.request else None
        super(MyBaseModelForm, self).__init__(*args, **kwargs)
        self.custom_init()


class ContactForm(MyBaseForm):
    full_name = forms.CharField(required=False)
    email = forms.EmailField()
    inquiry_type = forms.ChoiceField(choices=((1, "Comment"), (2, "Issue"), (3, "Request"), (4, "Question")))
    message = forms.CharField(widget=forms.Textarea, max_length=1000)


class SignUpForm(AllAuthSignUpForm, CustomFormMixin):

    first_name = forms.CharField(label="First Name", required=True, max_length=30)
    last_name = forms.CharField(label="Last Name", required=True, max_length=30)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.custom_init()


class SignInForm(LoginForm, CustomFormMixin):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SignInForm, self).__init__(*args, **kwargs)
        self.custom_init()
