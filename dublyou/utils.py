import datetime as dt
import geocoder as geo

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def upload_to_path(instance, filename):
    file_ext = filename.split(".")[-1]
    path = "img/{}/{}.{}".format(instance.__class__.__name__.tolower(),
                                 instance.id,
                                 file_ext)
    return path


def get_attr_mult(obj, attr):
    attrs = attr.split("__", 1)
    if isinstance(obj, dict):
        value = obj.get(attrs[0])
    else:
        value = getattr(obj, attrs[0])
    if len(attrs) == 1:
        return value
    return get_attr_mult(value, attrs[1])


def remove_items(ls1, ls2):
    return list(set(ls1) - set(ls2))


def record_string(wins, games_played):
    if games_played > 0:
        return "{}-{} ({} %)".format(wins, games_played - wins, round(wins / games_played, 3) * 100)


def get_city_state_from_zip(zip_code):
    location = geo.google(zip_code)
    return location.city, location.state


def get_location_from_zip(zip_code):
    location = geo.google(zip_code)
    return "{}, {}".format(location.city, location.state)


def send_notification(user, subject, message=None, template=None, instance=None, **kwargs):
    if template:
        ctx = kwargs
        ctx.update({"user": user,
                    "object": instance})
        message = render_to_string(template, ctx)
    else:
        message = message or ""
    params = {
        "subject": subject,
        "message": message,
        "from_email": settings.DEFAULT_FROM_EMAIL,
        "recipient_list": [user.email],
        "fail_silently": True
    }
    send_mail(**params)


def place_string(place):
    last_digit = int(str(place)[-1])
    endings = {1: "st", 2: "nd", 3: "rd"}
    ending = endings[last_digit] \
        if place not in range(11, 14) and last_digit in endings \
        else "th"
    return "{}{}".format(place, ending)


class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]
