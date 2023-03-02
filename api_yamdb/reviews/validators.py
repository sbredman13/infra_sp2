from datetime import datetime
from django.core.exceptions import ValidationError


def my_year_validator(value):
    if datetime.now().year < value < 1900:
        raise ValidationError('Не корректная дата!')
