from django.core.exceptions import ValidationError

from reviews.constants import RESERVED_USERNAME


def validate_not_me(value):
    """Валидатор, запрещающий использование username 'me'."""
    if value == RESERVED_USERNAME:
        raise ValidationError(
            f'Имя пользователя "{RESERVED_USERNAME}" запрещено.'
        )
