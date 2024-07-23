from core.utils.enums import ISODatePattern, TotalDegreePattern
from core.utils.messages import SERVICE_MESSSAGES
from core.utils.validators import Validators


class ValidationRules:
    @classmethod
    def student(self, student_basic_data):
        return [
            [
                Validators.required(),
                student_basic_data.get("studentNameAr"),
                "MISSING_STUDENT_NAME",
            ],
            [
                Validators.isLettersOnly(),
                student_basic_data.get("studentNameAr"),
                "INVALID_STUDENT_NAME_CHARACTERS",
            ],
            [
                Validators.maxLength(100),
                student_basic_data.get("studentNameAr"),
                "INVALID_STUDENT_NAME",
            ],
            [
                Validators.maxLength(20),
                student_basic_data.get("studentPassport"),
                "INVALID_PASSPORT_LENGTH",
            ],
            [
                Validators.maxLength(50),
                student_basic_data.get("studentMail"),
                "INVALID_EMAIL_FORMAT",
            ],
            [
                Validators.maxLength(250),
                student_basic_data.get("studentAddress"),
                "INVALID_ADDRESS_LENGTH",
            ],
            [
                Validators.regex(ISODatePattern),
                student_basic_data.get("studentBirthDate"),
                "INVALID_BIRTH_DATE",
            ],
        ]

    @classmethod
    def education_data(self, education_data):
        return [
            [
                Validators.maxLength(200),
                education_data.get("studentSchool"),
                "INVALID_SCHOOL_NAME_LENGTH",
            ],
            [
                Validators.maxLength(200),
                education_data.get("studentDept"),
                "INVALID_DEPT_LENGTH",
            ],
            [
                Validators.maxLength(9),
                education_data.get("studentSeatNumber"),
                "INVALID_SEATING_NUMBER_LENGTH",
            ],
            [
                Validators.isInteger(),
                education_data.get("studentSeatNumber"),
                "INVALID_SEATING_NUMBER",
            ],
            [
                Validators.regex(TotalDegreePattern),
                education_data.get("studentTot"),
                "INVALID_TOTAL_DEGREE",
            ],
            [
                Validators.regex(TotalDegreePattern),
                education_data.get("studentEquivTotscienceB"),
                "INVALID_TOTAL_EQUIV_DEGREE",
            ],
            [
                Validators.regex(TotalDegreePattern),
                education_data.get("studentSportDegree"),
                "INVALID_SPORT_DEGREE",
            ],
            [
                Validators.regex(TotalDegreePattern),
                education_data.get("studentComplainGain"),
                "INVALID_COMPLAIN_DEGREE",
            ],
        ]

    @classmethod
    def acceptance_data(self, acceptance_data):
        return [
            [
                Validators.required(False),
                acceptance_data.get("accept_studentTot"),
                "MISSING_ACCEPT_STUDENT_TOTAL",
            ],
            [
                Validators.required(False),
                acceptance_data.get("manualAddition"),
                "MISSING_MANUAL_ADDITION",
            ],
            [
                Validators.required(False),
                acceptance_data.get("accept_createdBy"),
                "MISSING_ACCEPT_CREATED_BY",
            ],
            [
                Validators.required(False),
                acceptance_data.get("accept_createdAt"),
                "MISSING_ACCEPT_CREATED_AT",
            ],
            [
                Validators.regex(ISODatePattern),
                acceptance_data.get("accept_createdAt"),
                "INVALID_CREATED_AT_DATE",
            ],
        ]

    @classmethod
    def student_tansiq_ids(self):
        return [
            {"key": "studentGender_id", "table": "gender", "required": False},
            {"key": "studentNationality_id", "table": "regions", "required": False},
            {"key": "studentReligion_id", "table": "religions", "required": False},
            {"key": "studentBirthPlace_id", "table": "regions", "required": False},
            {"key": "studentAddressPlace_id", "table": "regions", "required": False},
        ]

    @classmethod
    def education_tansiq_ids(self):
        return [
            {"key": "studentDeptCode_id", "table": "regions", "required": False},
            {
                "key": "studentSecondaryCert_id",
                "table": "certificates",
                "required": True,
            },
            {"key": "studentSchoolType_id", "table": "schooltype", "required": False},
            {"key": "year_id", "table": "years", "required": True},
            {"key": "studentCity_id", "table": "regions", "required": False},
            {
                "key": "studentSpecialization_id",
                "table": "studygroups",
                "required": True,
            },
        ]

    @classmethod
    def acceptance_tansiq_ids(self):
        return [
            {"key": "fac_id", "table": "faculties", "required": True},
            {"key": "semester_id", "table": "semesters", "required": True},
            {"key": "stage_id", "table": "stages", "required": True},
            {"key": "accept_year_id", "table": "years", "required": True},
            {"key": "univ_id", "table": "universities", "required": True},
            {"key": "registrationType", "table": "registrationtype", "required": True},
        ]

    @classmethod
    def validate_tansiq_ids(self, studentData, council_ids_map):
        return ValidationRules.validate_tansiq_ids_set(
            [
                {
                    "validation_set": ValidationRules.student_tansiq_ids(),
                    "data": studentData.get("student"),
                    "dict": "student",
                },
                {
                    "validation_set": ValidationRules.education_tansiq_ids(),
                    "data": studentData.get("studentEdu"),
                    "dict": "studentEdu",
                },
                {
                    "validation_set": ValidationRules.acceptance_tansiq_ids(),
                    "data": studentData.get("studentAcceptance"),
                    "dict": "studentAcceptance",
                },
            ],
            council_ids_map,
        )

    @classmethod
    def validate_acceptance_data_tansiq_ids(self, acceptance_data, council_ids_map):
        return ValidationRules.validate_tansiq_ids_set(
            [
                {
                    "validation_set": ValidationRules.acceptance_tansiq_ids(),
                    "data": acceptance_data,
                    "dict": "studentAcceptance",
                },
            ],
            council_ids_map,
        )

    @classmethod
    def validate_tansiq_ids_set(self, validations: list[dict], ids_map: dict):
        """
        Check if every tansiqid exists in council table, if exists replace
        tansiqid with council id otherwise return a message of the error

        Args:
            validations (list): list of dict contains validation_set and data
            ids_map (dict): dict of tables
                            every table is a dict of key: value => tansiqid: id

        Returns:
            dict: dict with success True or False, and a message if validation fails
        """
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
                        return {
                            "success": False,
                            "message": SERVICE_MESSSAGES.get(
                                "INVALID_TANSIQ_ID"
                            ).format(dict=validation.get("dict"), prop=item.get("key")),
                        }
                elif item.get("required", False):
                    return {
                        "success": False,
                        "message": SERVICE_MESSSAGES.get("MISSING_TANSIQ_ID").format(
                            dict=validation.get("dict"), prop=item.get("key")
                        ),
                    }

        return {"success": True}
