from core.utils.messages import SERVICE_MESSSAGES
from core.utils.validators import Validators


class ValidationRules:
    @classmethod
    def student(self, student_data):
        return [
            *ValidationRules.database_id(
                student_data.get("id"), "student", required=True
            ),
            *ValidationRules.gba(student_data.get("studentGraduationGPA")),
            *ValidationRules.database_id(
                student_data.get("studentGraduationGrade"), "graduation grade"
            ),
            *ValidationRules.percentage(
                student_data.get("studentGraduationPercentage")
            ),
            *ValidationRules.text_field(
                student_data.get("studentSpecialization"), "student specialization", 100
            ),
            *ValidationRules.text_field(
                student_data.get("studentDivision"), "student division", 100
            ),
            *ValidationRules.database_id(
                student_data.get("studentGraduationProjectGrade"),
                "graduation project grade",
            ),
            *ValidationRules.database_id(
                student_data.get("studentActualGraduationYear"),
                "actual graduation year id",
                required=True,
            ),
            *ValidationRules.database_id(
                student_data.get("studentActualGraduationMonth"),
                "actual graduation month id",
                required=True,
            ),
        ]

    @classmethod
    def database_id(self, value: float | str, key="generic", required=False):
        rules = [
            [
                Validators.isInteger(),
                value,
                SERVICE_MESSSAGES.get("INVALID_DB_ID").format(key=key),
            ],
            [
                Validators.min(0),
                value,
                SERVICE_MESSSAGES.get("INVALID_DB_ID").format(key=key),
            ],
        ]
        if required:
            rules.insert(
                1,
                [
                    Validators.required(),
                    value,
                    SERVICE_MESSSAGES.get("MISSING_DB_ID").format(key=key),
                ],
            )
        return rules

    @classmethod
    def gba(self, gba_value):
        return [
            [
                Validators.required(),
                gba_value,
                SERVICE_MESSSAGES.get("MISSING_KEY_VALUE").format(key="student gba"),
            ],
            [
                Validators.isFloat(),
                str(gba_value),
                SERVICE_MESSSAGES.get("INVALID_UNIV_GBA"),
            ],
            [
                Validators.min(0),
                gba_value,
                SERVICE_MESSSAGES.get("INVALID_UNIV_GBA"),
            ],
            [
                Validators.max(4),
                gba_value,
                SERVICE_MESSSAGES.get("INVALID_UNIV_GBA"),
            ],
        ]

    @classmethod
    def percentage(self, percentage):
        return [
            [
                Validators.isFloat(),
                str(percentage),
                SERVICE_MESSSAGES.get("INVALID_UNIV_PERCENTAGE"),
            ],
            [
                Validators.min(50),
                percentage,
                SERVICE_MESSSAGES.get("INVALID_UNIV_PERCENTAGE"),
            ],
            [
                Validators.max(100),
                percentage,
                SERVICE_MESSSAGES.get("INVALID_UNIV_PERCENTAGE"),
            ],
        ]

    @classmethod
    def text_field(self, value, key, max):
        return [
            [
                Validators.maxLength(max),
                value,
                SERVICE_MESSSAGES.get("INVALID_MAX_TEXT_FIELD").format(
                    key=key, max=max
                ),
            ],
        ]
