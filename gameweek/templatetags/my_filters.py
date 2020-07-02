from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


def currency(sterling):
    sterling = round(float(sterling), 2)
    return "$%s%s" % (intcomma(int(sterling)), ("%0.2f" % sterling)[-3:])


register.filter('currency', currency)


@register.filter
def percentage(value):
    return format(value, ".2%")
