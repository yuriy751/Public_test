# reset_inputs.py

from .input_fields import apply_input_fields
from .input_defaults import INPUT_DEFAULTS


def reset_inputs() -> None:
    """
    Сброс input-полей UI к значениям по умолчанию
    """
    apply_input_fields(INPUT_DEFAULTS.__dict__)
