from core.services.oldCouncilDataMigration.constants import (
    MESSAGES,
    SECONDARY_EDUCATION_IDS,
    STUDENT_VALIDATIONS_IDS,
    UNIVERSITY_EDUCATION_IDS,
)
from core.utils.enums import TotalDegreePattern
from core.utils.validators import Validators


class ValidationRules:
    @classmethod
    def student(self, student_basic_data):
        return [
            [
                Validators.isLettersOnly(),
                student_basic_data.get("studentNameAr"),
                {
                    "message": "INVALID_STUDENT_NAME_LETTERS",
                    "value": student_basic_data.get("studentNameAr"),
                    "flag": "studentNameAr",
                },
            ],
            [
                Validators.maxLength(100),
                student_basic_data.get("studentNameAr"),
                {
                    "message": "INVALID_STUDENT_NAME_LENGTH",
                    "value": student_basic_data.get("studentNameAr"),
                    "flag": "studentNameAr",
                },
            ],
            [
                Validators.minLength(4),
                (student_basic_data.get("studentNameAr") or "").strip().split(" "),
                {
                    "message": "INVALID_STUDENT_NAME_QUAD",
                    "value": student_basic_data.get("studentNameAr"),
                    "flag": "studentNameAr",
                },
            ],
            [
                Validators.required(),
                student_basic_data.get("studentNationality_id") or None,
                {
                    "message": "MISSING_NATIONALITY_ID",
                    "value": student_basic_data.get("studentNationality_id"),
                    "flag": "studentNationality_id",
                },
            ],
            [
                Validators.isNationalID(),
                student_basic_data.get("studentNID") or None,
                {
                    "message": "INVALID_NATIONAL_ID",
                    "value": student_basic_data.get("studentNID"),
                    "flag": "studentNID",
                },
            ],
            [
                Validators.maxLength(250),
                student_basic_data.get("studentAddress"),
                {
                    "message": "INVALID_ADDRESS_LENGTH",
                    "value": student_basic_data.get("studentAddress"),
                    "flag": "studentAddress",
                },
            ],
        ]

    @classmethod
    def secondary_education(self, secondary_education_data):
        return [
            [
                Validators.regex(TotalDegreePattern),
                secondary_education_data.get("studentTotalDegree"),
                {
                    "message": "INVALID_TOTAL_DEGREE",
                    "value": secondary_education_data.get("studentTotalDegree"),
                    "flag": "studentTotalDegree",
                },
            ],
            [
                Validators.regex(TotalDegreePattern),
                secondary_education_data.get("studentEquivTotalDegree"),
                {
                    "message": "INVALID_TOTAL_EQUIV_DEGREE",
                    "value": secondary_education_data.get("studentEquivTotalDegree"),
                    "flag": "studentEquivTotalDegree",
                },
            ],
        ]

    @classmethod
    def university_education(self, university_education_data):
        return [
            [
                Validators.isFloat(),
                str(university_education_data.get("studentGraduationGPA")),
                {
                    "message": "INVALID_UNIV_GPA",
                    "value": university_education_data.get("studentGraduationGPA"),
                    "flag": "studentGraduationGPA",
                },
            ],
            [
                Validators.min(0),
                university_education_data.get("studentGraduationGPA"),
                {
                    "message": "INVALID_UNIV_GPA",
                    "value": university_education_data.get("studentGraduationGPA"),
                    "flag": "studentGraduationGPA",
                },
            ],
            [
                Validators.max(4),
                university_education_data.get("studentGraduationGPA"),
                {
                    "message": "INVALID_UNIV_GPA",
                    "value": university_education_data.get("studentGraduationGPA"),
                    "flag": "studentGraduationGPA",
                },
            ],
            [
                Validators.isFloat(),
                str(university_education_data.get("studentGraduationPercentage")),
                {
                    "message": "INVALID_UNIV_PERCENTAGE",
                    "value": university_education_data.get(
                        "studentGraduationPercentage"
                    ),
                    "flag": "studentGraduationPercentage",
                },
            ],
            [
                Validators.min(50),
                university_education_data.get("studentGraduationPercentage"),
                {
                    "message": "INVALID_UNIV_PERCENTAGE",
                    "value": university_education_data.get(
                        "studentGraduationPercentage"
                    ),
                    "flag": "studentGraduationPercentage",
                },
            ],
            [
                Validators.max(100),
                university_education_data.get("studentGraduationPercentage"),
                {
                    "message": "INVALID_UNIV_PERCENTAGE",
                    "value": university_education_data.get(
                        "studentGraduationPercentage"
                    ),
                    "flag": "studentGraduationPercentage",
                },
            ],
            [
                Validators.isFloat(),
                university_education_data.get("TotalEquivalentHours"),
                {
                    "message": "INVALID_TOTAL_EQUIV_HOURS",
                    "value": university_education_data.get("TotalEquivalentHours"),
                    "flag": "TotalEquivalentHours",
                },
            ],
        ]

    @classmethod
    def validate_old_council_ids(self, student_data, council_ids_map):
        return ValidationRules.validate_old_council_ids_set(
            [
                {
                    "validation_set": STUDENT_VALIDATIONS_IDS,
                    "data": student_data.get("student"),
                    "dict": "student",
                },
                {
                    "validation_set": SECONDARY_EDUCATION_IDS,
                    "data": student_data.get("secondaryEdu"),
                    "dict": "secondaryEdu",
                },
                {
                    "validation_set": UNIVERSITY_EDUCATION_IDS,
                    "data": student_data.get("studentUniversityEdu"),
                    "dict": "studentUniversityEdu",
                },
            ],
            council_ids_map,
        )

    @classmethod
    def validate_old_council_ids_set(self, validations: list[dict], ids_map: dict):
        """
        Check if every `oldcouncilid`s exists in council table, if exists replace
        `oldcouncilid` with the new council id otherwise return messages of the errors

        Args:
            validations (list): list of dict contains validation_set and data
            ids_map (dict): dict of tables
                            every table is a dict of key: value => oldcouncilid: id

        Returns:
            dict: dict with success True or False, and error messages
        """
        success = True
        messages = []
        for validation in validations:
            validation_set = validation.get("validation_set")
            data = validation.get("data")

            for item in validation_set:
                id = data.get(item.get("key"), None)
                target_table = ids_map.get(item.get("table"))
                if id:
                    if str(id) in target_table:
                        data[item.get("key")] = target_table.get(str(id))
                    else:
                        success = False
                        id_key = validation.get("dict") + "." + item.get("key")
                        messages.append(
                            MESSAGES.get("INVALID_OLD_COUNCIL_ID").format(
                                dict=validation.get("dict"), prop=item.get("key")
                            )
                            + f", invalid id: {id_key}|value: {id}"
                        )

        return {"success": success, "messages": messages}
