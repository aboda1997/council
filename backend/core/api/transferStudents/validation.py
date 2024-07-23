from core.utils.enums import DateFormatPattern, FloatPattern
from core.utils.messages import EXCEPTIONS
from core.utils.validators import Validators


def get_validation_rules(
    student_id, faculty_id, transfer_date, equivalent_hours, transfer_level
):
    return [
        [
            Validators.required(),
            student_id,
            EXCEPTIONS.get("MISSING_STUDENT_ID"),
        ],
        [
            Validators.isInteger(),
            student_id,
            EXCEPTIONS.get("INVALID_STUDENT_ID"),
        ],
        [
            Validators.required(),
            faculty_id,
            EXCEPTIONS.get("MISSING_TRANSFER_FACULTY_ID"),
        ],
        [
            Validators.isInteger(),
            faculty_id,
            EXCEPTIONS.get("INVALID_TRANSFER_FACULTY_ID"),
        ],
        [
            Validators.regex(DateFormatPattern),
            transfer_date,
            EXCEPTIONS.get("INVALID_DATE_FORMAT"),
        ],
        [
            Validators.required(),
            equivalent_hours,
            EXCEPTIONS.get("MISSING_EQUIV_HOURS"),
        ],
        [
            Validators.isFloat(),
            equivalent_hours,
            EXCEPTIONS.get("INVALID_EQUIV_HOURS"),
        ],
        [
            Validators.regex(FloatPattern),
            str(equivalent_hours),
            EXCEPTIONS.get("INVALID_EQUIV_HOURS"),
        ],
        [
            Validators.min(0),
            equivalent_hours,
            EXCEPTIONS.get("INVALID_EQUIV_HOURS"),
        ],
        [
            Validators.required(),
            transfer_level,
            EXCEPTIONS.get("MISSING_TRANSFER_LEVEL"),
        ],
        [
            Validators.isInteger(),
            transfer_level,
            EXCEPTIONS.get("INVALID_TRANSFER_LEVEL"),
        ],
        [
            Validators.min(1),
            transfer_level,
            EXCEPTIONS.get("INVALID_TRANSFER_LEVEL"),
        ],
    ]
