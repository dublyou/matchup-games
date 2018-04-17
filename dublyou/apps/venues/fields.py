from django import forms
from django.core.validators import RegexValidator


class PhoneField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        # Define one message for all fields.
        error_messages = {
            'incomplete': 'Enter a country calling code and a phone number.',
        }
        # Or define a different message for each field.
        fields = (
            forms.CharField(
                error_messages={'incomplete': 'Enter a area code.'},
                validators=[
                    RegexValidator(r'^[0-9]{3}$', 'Enter a valid area code.'),
                ],
                max_length=3
            ),
            forms.CharField(
                error_messages={'incomplete': 'Enter a phone number.'},
                validators=[RegexValidator(r'^[0-9]{3}$', 'Enter a valid phone number.')],
                max_length=3
            ),
            forms.CharField(
                validators=[RegexValidator(r'^[0-9]{4}$', 'Enter a phone number.')],
                max_length=4
            ),
        )
        super(PhoneField, self).__init__(
            error_messages=error_messages, fields=fields,
            require_all_fields=False, *args, **kwargs
        )

    def compress(self, data_list):
        return "({}) {}-{}".format(data_list[0], data_list[1], data_list[2])


class HeightWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        if attrs:
            attrs.update({"class": attrs.get("class", "") + "form-control"})
        else:
            attrs = {"class": "form-control"}
        _widgets = (
            forms.widgets.Select(attrs=attrs, choices=((x, "{} ft".format(x)) for x in range(2, 8))),
            forms.widgets.Select(attrs=attrs, choices=((x, "{} in".format(x)) for x in range(0, 12))),
        )
        super(HeightWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            return [int(value/12), value % 12]
        return [6, 0]

    def format_output(self, rendered_widgets):
        return '<div class="input-group">{}</div>'.format(''.join(rendered_widgets))

    def value_from_datadict(self, data, files, name):
        data_list = [
            widget.value_from_datadict(data, files, name + '_%s' % i)
            for i, widget in enumerate(self.widgets)]
        return data_list


class HeightField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        self.widget = HeightWidget
        fields = (
            forms.ChoiceField(
                choices=((x, "{} ft") for x in range(2, 8))
            ),
            forms.ChoiceField(
                choices=((x, "{} in") for x in range(0, 12))
            ),
        )
        super(HeightField, self).__init__(
            fields=fields,
            require_all_fields=True, *args, **kwargs
        )

    def compress(self, data_list):
        return int(data_list[0]) * 12 + int(data_list[1])
