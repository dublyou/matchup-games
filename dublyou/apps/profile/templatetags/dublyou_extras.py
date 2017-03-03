from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def sub_space(value, char):
    return value.replace(char, " ")
