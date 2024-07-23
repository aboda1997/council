from datetime import datetime, timedelta

from core.utils.enums import (
    CertificateEnum,
    CountryEnum,
    DateFormatPattern,
    EmailPattern,
    FloatPattern,
    GradeEnum,
    StudentStatus,
    TotalDegreePattern,
    UniversityIdEnum,
)
from core.utils.messages import EXCEPTIONS, MESSAGES
from core.utils.validators import Validators


class ValidationsRules:
    @classmethod
    def student_ar_name(self, student_ar_name: str, name_length: int = 4):
        return [
            [
                Validators.required(),
                student_ar_name,
                MESSAGES.get("REQUIRED_STUDENT_NAME"),
            ],
            *ValidationsRules.student_name(student_ar_name, name_length),
        ]

    @classmethod
    def student_name(self, student_name: str, name_length: int = 4):
        return [
            [
                Validators.isLettersOnly(),
                student_name,
                EXCEPTIONS.get("INVALID_STUDENT_NAME_SYMBOLS"),
            ],
            [
                Validators.maxLength(126),
                student_name,
                EXCEPTIONS.get("INVALID_STUDENT_NAME_LENGTH"),
            ],
            [
                Validators.minLength(2),
                student_name,
                EXCEPTIONS.get("INVALID_STUDENT_NAMES_COUNT"),
            ],
            *ValidationsRules.student_name_parts(student_name, name_length),
        ]

    @classmethod
    def student_name_parts(self, student_name: str, name_length: int = 4):
        name_parts = student_name.split()
        rules = []
        for part in name_parts:
            rules.append(
                [
                    Validators.minLength(2),
                    part,
                    EXCEPTIONS.get('INVALID_STUDENT_NAME_SIZE'),
                ]
            )
        if len(name_parts) > 0:
            rules.append(
                [
                    Validators.minLength(name_length),
                    name_parts,
                    EXCEPTIONS.get(
                        "INVALID_STUDENT_FULL_NAME"
                        if name_length == 4
                        else "INVALID_STUDENT_NAMES_COUNT"
                    ),
                ],
            )
        return rules

    @classmethod
    def national_id(self, nid, required=False):
        rules = [
            [
                Validators.equalLength(14),
                nid,
                EXCEPTIONS.get("INVALID_NATIONAL_ID"),
            ],
            [
                Validators.isNationalID(),
                nid,
                EXCEPTIONS.get("INVALID_NATIONAL_ID"),
            ],
        ]
        if required:
            rules.insert(
                1,
                [
                    Validators.required(),
                    nid,
                    EXCEPTIONS.get("MISSING_NATIONAL_ID"),
                ],
            )
        return rules

    @classmethod
    def seat_number(self, seat_number):
        return [
            [
                Validators.maxLength(20),
                seat_number,
                EXCEPTIONS.get('INVALID_SEATING_NUMBER'),
            ],
            [
                Validators.isInteger(),
                seat_number,
                EXCEPTIONS.get('INVALID_SEATING_NUMBER'),
            ],
        ]

    @classmethod
    def passport(self, passport):
        return [
            [
                Validators.maxLength(20),
                passport,
                EXCEPTIONS.get('INVALID_PASSPORT_LENGTH'),
            ]
        ]

    @classmethod
    def student_status(self, status_id, required=True):
        rules = [
            [
                Validators.isInteger(),
                status_id,
                EXCEPTIONS.get("INVALID_STUDENT_STATUS_FK"),
            ],
        ]
        if required:
            rules.insert(
                1,
                [
                    Validators.required(),
                    status_id,
                    EXCEPTIONS.get("MISSING_STATUS_ID"),
                ],
            )
        return rules

    @classmethod
    def student_basic_data(self, student: dict[str:any], status_required: bool = True):
        # nid_required = (
        #     not student.get("studentNationality_id")
        #     or int(student.get("studentNationality_id")) == CountryEnum.EGYPT.value
        # )
        nid_required = False
        return [
            *ValidationsRules.national_id(student.get("studentNID"), nid_required),
            *ValidationsRules.passport(student.get("studentPassport")),
            [
                Validators.regex(DateFormatPattern),
                student.get("studentBirthDate"),
                EXCEPTIONS.get("INVALID_DATE_FORMAT"),
            ],
            [
                Validators.minDate(datetime(1900, 1, 1)),
                student.get("studentBirthDate"),
                EXCEPTIONS.get("INVALID_BIRTH_DATE_RANGE"),
            ],
            [
                Validators.maxDate(datetime.now() - timedelta(days=365 * 10)),
                student.get("studentBirthDate"),
                EXCEPTIONS.get("INVALID_BIRTH_DATE_RANGE"),
            ],
            [
                Validators.maxLength(200),
                student.get("studentAddress"),
                EXCEPTIONS.get("INVALID_STUDENT_ADDRESS_LENGTH"),
            ],
            [
                Validators.isInteger(),
                student.get("studentPhone"),
                EXCEPTIONS.get("INVALID_PHONE_FORMAT"),
            ],
            [
                Validators.maxLength(20),
                student.get("studentPhone"),
                EXCEPTIONS.get("INVALID_PHONE_FORMAT"),
            ],
            [
                Validators.regex(EmailPattern),
                student.get("studentMail"),
                EXCEPTIONS.get("INVALID_EMAIL_FORMAT"),
            ],
            [
                Validators.maxLength(75),
                student.get("studentMail"),
                EXCEPTIONS.get("INVALID_EMAIL_LENGTH"),
            ],
            [
                Validators.isInteger(),
                student.get("studentNationality_id"),
                EXCEPTIONS.get("INVALID_NATIIONALITY_FK"),
            ],
            [
                Validators.isInteger(),
                student.get("studentAddressPlaceGov_id"),
                EXCEPTIONS.get("INVALID_ADDRESS_GOVERNORATES_FK"),
            ],
            [
                Validators.isInteger(),
                student.get("studentBirthPlaceGov_id"),
                EXCEPTIONS.get("INVALID_BIRTH_GOVERNORATES_FK"),
            ],
            [
                Validators.isInteger(),
                student.get("studentReligion_id"),
                EXCEPTIONS.get("INVALID_RELIGION_FK"),
            ],
            [
                Validators.isInteger(),
                student.get("studentGender_id"),
                EXCEPTIONS.get("INVALID_GENDER_FK"),
            ],
            *ValidationsRules.student_status(
                student.get("studentStatus_id"), status_required
            ),
            [
                Validators.maxLength(500),
                student.get("notes"),
                EXCEPTIONS.get("INVALID_STUDENT_NOTES_LENGTH"),
            ],
        ]

    @classmethod
    def student_sec_edu_data(
        self, student_sec_data: dict[str:any], student_certificate, student_status
    ):
        rules = [
            [
                Validators.isInteger(),
                student_sec_data.get("studentCertificateYear_id"),
                EXCEPTIONS.get("INVALID_YEAR_FK"),
            ],
            [
                Validators.isInteger(),
                student_sec_data.get("studentSecondaryCert_id"),
                EXCEPTIONS.get("INVALID_CERTIFICATE_FK"),
            ],
            [
                Validators.isInteger(),
                student_sec_data.get("studentStudyGroup_id"),
                EXCEPTIONS.get("INVALID_STUDY_GROUP_FK"),
            ],
            [
                Validators.isInteger(),
                student_sec_data.get("studentFulfillment_id"),
                EXCEPTIONS.get("INVALID_FULFILLMENT_FK"),
            ],
        ]
        if (
            student_sec_data
            and student_certificate != CertificateEnum.EGYPTIAN_GENERAL_SECONADARY.value
        ):
            rules = [
                [
                    Validators.required(),
                    student_sec_data.get("studentSecondaryCert_id"),
                    EXCEPTIONS.get("MISSING_CERT_ID"),
                ],
                [
                    Validators.required(),
                    student_sec_data.get("studentCertificateYear_id"),
                    EXCEPTIONS.get("MISSING_CERT_YEAR"),
                ],
                *rules,
            ]
        if str(student_status or "") == str(StudentStatus.FULFILLMENT.value):
            rules.append(
                [
                    Validators.required(),
                    student_sec_data.get("studentFulfillment_id"),
                    EXCEPTIONS.get("MISSING_FULFILLMENT_ID"),
                ]
            )
        return rules

    @classmethod
    def student_degree(self, student_sec_data: dict[str:any], student_certificate):
        rules = [
            [
                Validators.regex(TotalDegreePattern),
                str(student_sec_data.get("studentTot") or ""),
                EXCEPTIONS.get("INVALID_TOTAL_GRADE"),
            ],
            [
                Validators.regex(TotalDegreePattern),
                str(student_sec_data.get("studentEquivTot") or ""),
                EXCEPTIONS.get("INVALID_TOTAL_EQV_GRADE"),
            ],
            [
                Validators.regex(TotalDegreePattern),
                str(student_sec_data.get("studentSportDegree") or ""),
                EXCEPTIONS.get("INVALID_SPORT_DEGREE"),
            ],
            [
                Validators.regex(TotalDegreePattern),
                str(student_sec_data.get("studentComplainGain") or ""),
                EXCEPTIONS.get("INVALID_COMPLIAN_DEGREE"),
            ],
        ]
        if (
            student_sec_data
            and student_certificate != CertificateEnum.EGYPTIAN_GENERAL_SECONADARY.value
        ):
            rules = [
                [
                    Validators.required(),
                    student_sec_data.get("studentEquivTot"),
                    EXCEPTIONS.get("MISSING_TOTAL_EQV_GRADE"),
                ],
                *rules,
            ]
        return rules

    @classmethod
    def add_student_sec_edu_data(self, student_sec_data):
        rules = [
            *ValidationsRules.database_id(
                student_sec_data.get("studentSecondaryCert_id"),
                "Secondary certificate",
                "شهادة الثانوية",
                required=True,
            ),
            *ValidationsRules.database_id(
                student_sec_data.get("studentCertificateYear_id"),
                "Secondary certificate year",
                "عام الحصول على الشهادة الثانوية",
                required=True,
            ),
            *ValidationsRules.database_id(
                student_sec_data.get("studentStudyGroup_id"),
                "Secondary study group branch",
                "شعبة الثانوية",
                required=True,
            ),
            [
                Validators.maxLength(9),
                str(student_sec_data.get("studentSeatNumber")),
                EXCEPTIONS.get("INVALID_SEATING_NUMBER"),
            ],
        ]
        if (
            student_sec_data
            and student_sec_data.get("studentSecondaryCert_id")
            == CertificateEnum.EGYPTIAN_GENERAL_SECONADARY.value
        ):
            rules = [
                [
                    Validators.required(),
                    student_sec_data.get("studentTot"),
                    EXCEPTIONS.get("MISSING_TOTAL_GRADE"),
                ],
                *rules,
            ]
        return rules

    @classmethod
    def student_uni_edu_data(self, student_uni_data: dict[str:any]):
        return [
            [
                Validators.isInteger(),
                student_uni_data.get("studentExpectedGraduationYear_id"),
                EXCEPTIONS.get("INVALID_GRADUATION_YEAR_FK"),
            ],
            [
                Validators.isInteger(),
                student_uni_data.get("studentExpectedGraduationMonth_id"),
                EXCEPTIONS.get("INVALID_GRADUATION_MONTH_FK"),
            ],
            [
                Validators.isInteger(),
                student_uni_data.get("studentLevel_id"),
                EXCEPTIONS.get("INVALID_TRANSFER_LEVEL"),
            ],
            [
                Validators.min(1),
                student_uni_data.get("studentLevel_id"),
                EXCEPTIONS.get("INVALID_TRANSFER_LEVEL"),
            ],
            [
                Validators.isInteger(),
                student_uni_data.get("transferFulfillment_id"),
                EXCEPTIONS.get("INVALID_FULFILLMENT_FK"),
            ],
            [
                Validators.min(1),
                student_uni_data.get("transferFulfillment_id"),
                EXCEPTIONS.get("INVALID_FULFILLMENT_FK"),
            ],
            [
                Validators.isFloat(),
                student_uni_data.get("totalEquivalentHours"),
                EXCEPTIONS.get("INVALID_EQUIV_HOURS"),
            ],
            [
                Validators.regex(FloatPattern),
                str(student_uni_data.get("totalEquivalentHours") or ""),
                EXCEPTIONS.get("INVALID_EQUIV_HOURS"),
            ],
        ]

    @classmethod
    def add_student_uni_edu_data(self, student_uni_data: dict[str:any]):
        is_external_university = (
            student_uni_data.get("studentUniveristy_id")
            == UniversityIdEnum.EXTERNAL.value
        )
        return [
            *ValidationsRules.database_id(
                student_uni_data.get("studentRegistrationType_id"),
                "Registration type",
                "نوع التسجيل",
                required=True,
            ),
            *ValidationsRules.database_id(
                student_uni_data.get("studentEnrollYear_id"),
                "University enrollment year",
                "عام الالتحاق بالجامعة",
                required=True,
            ),
            *ValidationsRules.database_id(
                student_uni_data.get("studentEnrollSemester_id"),
                "University enrollment semester",
                "الفصل الدراسي الالتحاق بالجامعة",
                required=True,
            ),
            *ValidationsRules.database_id(
                student_uni_data.get("studentEnrollStage_id"),
                "University enrollment stage",
                "عام الالتحاق بالجامعة",
                required=True,
            ),
            *ValidationsRules.database_id(
                student_uni_data.get("studentUniveristy_id"),
                "Enrollment university",
                "الجامعة الملحق بها",
                required=True,
            ),
            *ValidationsRules.database_id(
                student_uni_data.get("studentFaculty_id"),
                "Entrollment faculty",
                "الكلية الملحق بها",
                required=(not is_external_university),
            ),
            *ValidationsRules.text_field(
                student_uni_data.get("studentCustomUniversityFaculty"),
                200,
                "External University and Faculty Name",
                "اسم الجامعة والكلية الخارجية",
                required=is_external_university,
            ),
        ]

    @classmethod
    def graduation_data(self, student_data):
        return [
            *ValidationsRules.gpa(student_data.get("studentGraduationGPA")),
            *ValidationsRules.database_id(
                student_data.get("studentGraduationGrade_id"),
                "graduation grade",
                "تقدير التخرج",
            ),
            *ValidationsRules.isNotFailingGrade(
                student_data.get("studentGraduationGrade_id"),
                "graduation grade",
                "تقدير التخرج",
            ),
            *ValidationsRules.percentage(
                student_data.get("studentGraduationPercentage")
            ),
            *ValidationsRules.equiv_hours(
                student_data.get("studentGraduationEquivalentHours")
            ),
            *ValidationsRules.text_field(
                student_data.get("studentSpecialization"),
                100,
                "student specialization",
                "التخصص",
            ),
            *ValidationsRules.text_field(
                student_data.get("studentDivision"), 100, "student division", "القسم"
            ),
            *ValidationsRules.database_id(
                student_data.get("studentGraduationProjectGrade_id"),
                "graduation project grade",
                "تقدير مشروع التخرج",
            ),
            *ValidationsRules.isNotFailingGrade(
                student_data.get("studentGraduationProjectGrade_id"),
                "graduation project grade",
                "تقدير مشروع التخرج",
            ),
            *ValidationsRules.database_id(
                student_data.get("studentActualGraduationYear_id"),
                "actual graduation year id",
                "عام التخرج",
                required=True,
            ),
            *ValidationsRules.database_id(
                student_data.get("studentActualGraduationMonth_id"),
                "actual graduation month id",
                "شهر التخرج",
                required=True,
            ),
        ]

    @classmethod
    def review_initally_accepted(self, data):
        has_fulfillment = str(data.get("studentStatus")) == str(
            StudentStatus.FULFILLMENT.value
        )
        rules = [
            [
                Validators.required(),
                data.get("studentsIds"),
                EXCEPTIONS.get("MISSING_STUDENT_IDS"),
            ],
            [
                Validators.minLength(1),
                data.get("studentsIds"),
                EXCEPTIONS.get("INVALID_STUDENT_IDS_LENGTH"),
            ],
            [
                Validators.maxLength(100),
                data.get("studentsIds"),
                EXCEPTIONS.get("INVALID_STUDENT_IDS_LENGTH"),
            ],
            *ValidationsRules.database_id(
                data.get("studentStatus"), "Students Status", "حالة الطلاب", True
            ),
            [
                Validators.isIn(
                    [
                        str(StudentStatus.ACCEPTED.value),
                        str(StudentStatus.FULFILLMENT.value),
                        str(StudentStatus.REJECTED.value),
                    ]
                ),
                str(data.get("studentStatus")),
                EXCEPTIONS.get("STUDENT_STATUS_OUTSIDE_ALLOWED"),
            ],
            *ValidationsRules.database_id(
                data.get("studentFulfillment"),
                "Student Fulfillment Reason",
                "سبب الاسيتفاء للطلاب",
                has_fulfillment,
            ),
        ]
        for id in data.get("studentsIds", []):
            rules.extend(ValidationsRules.database_id(id, "student", "الطالب", True))
        return []

    @classmethod
    def database_id(
        self, value: float | str, keyEn="generic", keyAr="عادى", required=False
    ):
        rules = [
            [
                Validators.isInteger(),
                value,
                EXCEPTIONS.get("INVALID_DB_ID").format(keyEn=keyEn, keyAr=keyAr),
            ],
            [
                Validators.min(0),
                value,
                EXCEPTIONS.get("INVALID_DB_ID").format(keyEn=keyEn, keyAr=keyAr),
            ],
        ]
        if required:
            rules.insert(
                1,
                [
                    Validators.required(),
                    value,
                    EXCEPTIONS.get("MISSING_DB_ID").format(keyEn=keyEn, keyAr=keyAr),
                ],
            )
        return rules

    @classmethod
    def isNotFailingGrade(self, value: float | str, keyEn="generic", keyAr="عادى"):
        rules = [
            [
                Validators.isNotIn(GradeEnum.FAILING_GRADES.value),
                value,
                EXCEPTIONS.get("INVALID_DB_ID").format(keyEn=keyEn, keyAr=keyAr),
            ],
        ]
        return rules

    @classmethod
    def gpa(self, gpa_value):
        return [
            [
                Validators.required(),
                gpa_value,
                EXCEPTIONS.get("MISSING_KEY_VALUE").format(
                    keyEn="student gpa", keyAr="المعدل التراكمي"
                ),
            ],
            [
                Validators.isFloat(),
                str(gpa_value),
                EXCEPTIONS.get("INVALID_UNIV_GPA"),
            ],
            [
                Validators.min(0),
                gpa_value,
                EXCEPTIONS.get("INVALID_UNIV_GPA"),
            ],
            [
                Validators.max(4),
                gpa_value,
                EXCEPTIONS.get("INVALID_UNIV_GPA"),
            ],
        ]

    @classmethod
    def percentage(self, percentage):
        return [
            [
                Validators.isFloat(),
                str(percentage),
                EXCEPTIONS.get("INVALID_UNIV_PERCENTAGE"),
            ],
            [
                Validators.min(50),
                percentage,
                EXCEPTIONS.get("INVALID_UNIV_PERCENTAGE"),
            ],
            [
                Validators.max(100),
                percentage,
                EXCEPTIONS.get("INVALID_UNIV_PERCENTAGE"),
            ],
        ]

    @classmethod
    def equiv_hours(self, hours):
        return [
            [
                Validators.isFloat(),
                str(hours),
                EXCEPTIONS.get("INVALID_EQUIV_HOURS"),
            ],
            [
                Validators.min(0),
                hours,
                EXCEPTIONS.get("INVALID_EQUIV_HOURS"),
            ],
        ]

    @classmethod
    def text_field(self, value, max, keyEn="generic", keyAr="عادى", required=False):
        rules = [
            [
                Validators.maxLength(max),
                value,
                EXCEPTIONS.get("INVALID_MAX_TEXT_FIELD").format(
                    keyEn=keyEn, keyAr=keyAr, max=max
                ),
            ],
        ]
        if required:
            rules.insert(
                1,
                [
                    Validators.required(),
                    value,
                    EXCEPTIONS.get("MISSING_KEY_VALUE").format(
                        keyEn=keyEn, keyAr=keyAr
                    ),
                ],
            )
        return rules
