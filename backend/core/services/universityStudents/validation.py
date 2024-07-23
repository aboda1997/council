from core.utils.messages import SERVICE_MESSSAGES
from core.utils.validators import Validators


class ValidationRules:
    @classmethod
    def studentFilters(self, student_filter):
        faculty_id = student_filter.get("facultyId")
        university_id = student_filter.get("univeristyId")
        rules = [
            [
                Validators.isInteger(),
                faculty_id,
                SERVICE_MESSSAGES.get("INVALID_STUDENT_FACULTY_FILTER"),
            ],
            [
                Validators.isInteger(),
                university_id,
                SERVICE_MESSSAGES.get("INVALID_STUDENT_UNIVERISTY_FILTER"),
            ],
            [
                Validators.isInteger(),
                student_filter.get("page"),
                SERVICE_MESSSAGES.get("INVALID_STUDENT_PAGE_FILTER"),
            ],
            [
                Validators.min(0),
                student_filter.get("page"),
                SERVICE_MESSSAGES.get("INVALID_STUDENT_PAGE_FILTER"),
            ],
            [
                Validators.isInteger(),
                student_filter.get("perPage"),
                SERVICE_MESSSAGES.get("INVALID_STUDENT_PER_PAGE_FILTER"),
            ],
            [
                Validators.min(1),
                student_filter.get("perPage"),
                SERVICE_MESSSAGES.get("INVALID_STUDENT_PER_PAGE_FILTER"),
            ],
            [
                Validators.max(200),
                student_filter.get("perPage"),
                SERVICE_MESSSAGES.get("INVALID_STUDENT_PER_PAGE_FILTER"),
            ],
        ]
        if not faculty_id:
            rules.insert(
                1,
                [
                    Validators.required(),
                    university_id,
                    SERVICE_MESSSAGES.get("MISSING_STUDENT_FACULTY_FILTER"),
                ],
            )
        else:
            rules.insert(
                1,
                [
                    Validators.required(),
                    faculty_id,
                    SERVICE_MESSSAGES.get("MISSING_STUDENT_UNIVERISTY_FILTER"),
                ],
            )
        return rules
