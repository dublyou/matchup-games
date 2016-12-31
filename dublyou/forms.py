from django import forms
# from django.utils.translation import ugettext_lazy as _
from .constants import DEFAULT_INPUT_CLASSES, INPUT_HTML_OUTPUT
import re
from allauth.account.forms import SignupForm


class CustomFormMixin(object):
    dependent_inputs = None

    def custom_init(self):
        for name, field in self.fields.items():
            field.label = field.label or name.title().replace("_", " ")
            field.widget.attrs.update({
                'class': DEFAULT_INPUT_CLASSES,
                'placeholder': field.label
            })

        if self.dependent_inputs:
            for input_tree in self.dependent_inputs:
                self.add_action_classes(input_tree)

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

    def add_action_classes(self, input_tree, action_class=None):
        input_name = input_tree["name"]
        if "fields" in input_tree:
            self.fields[input_name].widget.attrs.update({
                'onchange': "$(this).triggerAction()"
            })
            dependents = {}
            recurse = []
            for value, ls in input_tree["fields"]:
                for dependent_field in ls:
                    if type(dependent_field) == dict:
                        field_name = dependent_field["name"]

                    if dependent_field in dependents:
                        dependents[field_name] += "--" + str(value)
                    else:
                        dependents[field_name] = str(value)
                        if type(dependent_field) == dict:
                            recurse.append(field_name)

            for field_name, value in dependents.items():
                classes = self.fields[field_name].widget.attrs["class"] + " " + action_class
                self.fields[field_name].widget.attrs.update({
                    'class': classes + "__action__" + input_name + "__" + value
                })

            for field_name in recurse:
                self.add_action_classes(input_tree["fields"][field_name],
                                        "__action__" + input_name + "__" + dependents[field_name])


class MyBaseForm(forms.Form, CustomFormMixin):
    def __init__(self, *args, **kwargs):
        super(MyBaseForm, self).__init__(*args, **kwargs)
        self.custom_init()


class MyBaseModelForm(forms.ModelForm, CustomFormMixin):
    def __init__(self, *args, **kwargs):
        super(MyBaseModelForm, self).__init__(*args, **kwargs)
        self.custom_init()


class ContactForm(MyBaseForm):
    full_name = forms.CharField(required=False)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea, max_length=1000)


class MySignupForm(SignupForm, CustomFormMixin):

    first_name = forms.CharField(label="First Name", required=True, max_length=30)
    last_name = forms.CharField(label="Last Name", required=True, max_length=30)

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.custom_init()