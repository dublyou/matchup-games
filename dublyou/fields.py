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


class TimeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        if attrs:
            attrs.update({"class": attrs.get("class", "") + "form-control"})
        else:
            attrs = {"class": "form-control"}
        _widgets = (
            forms.widgets.Select(attrs=attrs, choices=((x, x) for x in range(1, 13))),
            forms.widgets.Select(attrs=attrs, choices=(("%02d" % (x,), ":%02d" % (x,)) for x in range(0, 60))),
            forms.widgets.Select(attrs=attrs, choices=(("AM", "AM"), ("PM", "PM"))),
        )
        super(TimeWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            am_pm = "PM" if value.hour > 11 else "AM"
            hour = value.hour % 12
            hour = hour if hour > 0 else 12
            return [hour, value.minute, am_pm]
        return ["", "", ""]

    def format_output(self, rendered_widgets):
        return '<div class="input-group">{}</div>'.format(''.join(rendered_widgets))

    def value_from_datadict(self, data, files, name):
        data_list = [
            widget.value_from_datadict(data, files, name + '_%s' % i)
            for i, widget in enumerate(self.widgets)]
        return data_list


class MultiTimeField(forms.MultiValueField, forms.TimeField):
    def __init__(self, *args, **kwargs):
        self.widget = TimeWidget
        fields = (
            forms.ChoiceField(
                choices=((x, x) for x in range(1, 13))
            ),
            forms.ChoiceField(
                choices=(("%02d" % (x,), "%02d" % (x,)) for x in range(0, 60))
            ),
            forms.ChoiceField(
                choices=(("AM", "AM"), ("PM", "PM"))
            ),
        )
        super(MultiTimeField, self).__init__(
            fields=fields,
            require_all_fields=True, *args, **kwargs
        )

    def compress(self, data_list):
        if data_list:
            hour = int(data_list[0])
            minute = data_list[1]
            hour = (0 if hour == 12 else hour) + (12 if data_list[2] == "PM" else 0)
            return self.to_python("{}:{}:00".format(hour, minute))