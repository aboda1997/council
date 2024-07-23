FACULTIES_REMOTE_URL = "http://193.227.50.217/NewSU/libraries/FuAPI.aspx?fn=AOPU_API&faculty_id={faculty_id}"
FACULTIES_LOCAL_URL = "http://localhost:3333/students/{faculty_id}"

MODES: dict[str, str] = {
    "REPORT": "report",
    "STORE": "store",
    "TEST": "test",
}

FLAGS: dict[str, str] = {
    "REPEATED_STUDENT": "repeated_student",
    "FULL_STUDENT_DATA": "output_fullData",
}

DEFAULT_MODE = MODES.get("REPORT")
DEFAULT_FLAGS = [
    "repeated_student" "output_fullData" "id",
    "studentNID",
    "studentNameAr",
    "studentPhone",
    "studentAddress",
    "notes",
    "studentNationality_id",
    "studentTotalDegree",
    "studentEquivTotalDegree",
    "certificateYear_id",
    "studentDeptCode_id",
    "studentSecondaryCert_id",
    "studentEnrollStage_id",
    "studentEnrollYear_id",
    "studentFaculty_id",
    "studentGraduationMonth_id",
    "studentGraduationYear_id",
    "studentGraduationGPA",
    "studentGraduationGrade_id",
    "studentGraduationPercentage",
    "studentDivision",
    "studentGraduationProjectGrade_id",
    "studentSpecialization",
    "AcceptanceStatus",
    "RegistrationTypeID",
    "TotalEquivalentHours",
    "OriginalUniID",
    "OriginalFacultyID",
]

# ----- * ----- * -----

MESSAGES: dict[str, str] = {
    "INVALID_JSON_FORMAT": "Invalid JSON format",
    "INVALID_DATA_FORMAT": "Invalid data format, data must have students array",
    "CONNECTION_FAILURE": "Failed to establish a new connection",
    "FACULTY_NOT_FOUND": "No faculty found with id: {faculty_id}",
    "INVALID_STUDENT_FORMAT": "Invalid student format, every student must contain student, secondaryEdu, and studentUniversityEdu",
    "MISSING_STUDENT_ID": "Missing student id, student id is required",
    "MISSING_NATIONALITY_ID": "Missing nationality id, nationality id is required",
    "MISSING_NATIONAL_ID": "Missing national id, national id is required for egyptian students",
    "STUDENT_ALREADY_EXISTS": "Student already exists with newer date",
    "STUDENT_ALREADY_EXISTS_REPLACE": "Student already exists and will be replaced",
    "STUDENT_REPLACED": "Student exists but had been replaced",
    "STUDENT_NOT_FOUND": "Student not found",
    "CAN_NOT_UPDATE_STUDENT": "Can not update student, student status is not withdrawn",
    "MISSING_CERT_ID": "Missing id `secondaryEdu.studentSecondaryCert_id`",
    "MISSING_TOTAL_DEGREE": "Missing total degree, `secondaryEdu.studentTotalDegree` is required for GS students",
    "MISSING_EQUIV_DEGREE": "Missing equivalent total degree, `secondaryEdu.studentEquivTotalDegree` is required for non GS students",
    "INVALID_STUDENT_NAME_LETTERS": "Invalid student name, student name does not contain letters only",
    "INVALID_STUDENT_NAME_LENGTH": "Invalid student name, student name exceeds 100 letters",
    "INVALID_STUDENT_NAME_QUAD": "Invalid student name, student name is not quadrilateral",
    "INVALID_NATIONAL_ID": "Invalid national id, found {national_id} and set to null",
    "INVALID_PASSPORT_LENGTH": "Passport id number must not exceed 20 characters",
    "INVALID_EMAIL_FORMAT": "Invalid student email address",
    "INVALID_ADDRESS_LENGTH": "Address must not exceed 250 characters",
    "INVALID_TOTAL_DEGREE": "Invalid student total degree, must be a number with maximum 3 integer numbers and 3 floating numbers",
    "INVALID_TOTAL_EQUIV_DEGREE": "Invalid student equivalent total degree, must be a number with maximum 3 integer numbers and 3 floating numbers",
    "INVALID_UNIV_GPA": "Invalid student GPA, must be a positive number between 0 and 4 with a maximum of 3 decimal numbers",
    "INVALID_PHONE_FORMAT": "Invalid student phone number",
    "INVALID_UNIV_PERCENTAGE": "Invalid student percentage, must be a positive number between 50 and 100 with a maximum of 3 decimal numbers",
    "INVALID_TOTAL_EQUIV_HOURS": "Invalid total equivalent hours, must be a number",
    "INVALID_OLD_COUNCIL_ID": "Invalid id, `{dict}.{prop}` does exist in the council",
    "MISSING_OLD_COUNCIL_ID": "Missing id, `{dict}.{prop}` is required",
    "UNEXPECTED_DB_ERROR": "Student did not stored due to unexpected db error",
    "MISMATCHING_VALUES": "Mismatching values, table: `{table}`, prop: `{prop}`, received: `{received}`|expected to be: `{formatted}`|but found: `{found}`",
    "STUDENT_NOT_FOUND": "Student not found",
    "STUDENT_RECORDS_NOT_FOUND": "Student education records not found",
    "PERCENT_FOUND_IN_GPA": "A percent sign (%) is found in the GPA, value is set to graduation percentage instead",
    "NOTES_UPDATE": "`DB Entry` is found and removed from notes",
}

# ----- * ----- * -----

STAGE_MAPPING = [
    {"stage_id": [1, 7], "semester": 1, "stage": 1},
    {"stage_id": [2], "semester": 1, "stage": 2},
    {"stage_id": [3], "semester": 1, "stage": 3},
    {"stage_id": [4], "semester": 2, "stage": 1},
    # the rest 5->26 except (7)
    {"stage_id": list(range(5, 27)), "semester": 2, "stage": 6},
]

STAGE_NOTES = {
    "5": "لجنة فحص الأوراق",
    "6": "لجنة حل المشاكل",
    "8": "الفصل الدراسى الاول (نسبة 10%)",
    "9": "الفصل الدراسى الاول (طلاب معهد الجزيرة)",
    "10": "الفصل الدراسى الاول (الشهادات المعادلة)",
    "11": "الفصل الدراسى الثانى (نسبة 10%)",
    "12": "الفصل الدراسى الثانى (طلاب معهد الجزيرة",
    "13": "الفصل الدراسى الثانى (الاعداد المضافة)",
    "14": "مرحلة الامتياز",
    "15": "الفصل الدراسى الاول (نسبة 3.5%)",
    "16": "الفصل الدراسى الاول (نسبة 1.5%)",
    "17": "الفصل الدراسى الاول (منح دراسية )",
    "18": "الفصل الدراسى الاول (نسبة 2% تنسيق الكت",
    "19": "الفصل الدراسى الاول (الطلاب السوريين)",
    "20": "الفصل الدراسى الاول (الاعداد المضافة)",
    "21": "الفصل الدراسى الثانى (نسبة 3.5%)",
    "22": "الفصل الدراسى الثانى (نسبة 1.5%)",
    "23": "الفصل الدراسى الثانى (منح دراسية )",
    "24": "الفصل الدراسى الثانى (الطلاب السوري ين)",
    "25": "الكل",
    "26": "الفصل الدراسى الأول -محولين جامعة العاش",
}

# ----- * ----- * -----

STUDENT_VALIDATIONS_IDS = [
    {"key": "studentGender_id", "table": "gender"},
    {"key": "studentNationality_id", "table": "regions"},
]

SECONDARY_EDUCATION_IDS = [
    {"key": "certificateYear_id", "table": "years"},  # True
    # `studentDeptCode_id` comes from the old council as `study group` `الشعبة`
    {"key": "studentDeptCode_id", "table": "studygroups"},
    {"key": "studentSecondaryCert_id", "table": "certificates"},
]

UNIVERSITY_EDUCATION_IDS = [
    {"key": "studentEnrollYear_id", "table": "years"},
    {"key": "studentFaculty_id", "table": "faculties"},
    {"key": "studentGraduationMonth_id", "table": "months"},
    {"key": "studentGraduationYear_id", "table": "years"},
    {"key": "studentGraduationGrade_id", "table": "grades"},
    {"key": "studentGraduationProjectGrade_id", "table": "grades"},
    {"key": "AcceptanceStatus", "table": "status"},
    {"key": "UserID", "table": "users"},
    {"key": "RegistrationTypeID", "table": "registrationtype"},
    {"key": "OriginalFacultyID", "table": "faculties"},
    {"key": "OriginalUniID", "table": "universities"},
]

# ----- * ----- * -----

STUDENT_ATTRIBUTES = [
    "studentNID",
    "studentPhone",
    "studentAddress",
    "notes",
    "migration_notes",
    "uniqueId",
    "studentBirthDate",
    # Ids
    "studentGender_id",
    "studentNationality_id",
    "studentStatus_id",
]

SECONDARY_EDUCATION_MAPPING = [
    ["studentTotalDegree", "studentTot"],
    ["studentEquivTotalDegree", "studentEquivTot"],
    # Ids
    ["certificateYear_id", "studentCertificateYear_id"],
    # `studentDeptCode_id` comes from the old council as `study group` `الشعبة`
    ["studentDeptCode_id", "studentStudyGroup_id"],
    ["studentSecondaryCert_id", "studentSecondaryCert_id"],
]

UNIVERSITY_EDUCATION_MAPPING = [
    ["studentGraduationGPA", "studentGraduationGPA"],
    ["studentGraduationPercentage", "studentGraduationPercentage"],
    ["studentDivision", "studentDivision"],
    ["studentSpecialization", "studentSpecialization"],
    ["TotalEquivalentHours", "totalEquivalentHours"],
    ["transferDate", "transferDate"],
    ["studentTot", "studentTot"],
    # Ids
    ["studentFaculty_id", "studentFaculty_id"],
    ["studentUniveristy_id", "studentUniveristy_id"],
    ["studentEnrollYear_id", "studentEnrollYear_id"],
    ["studentGraduationMonth_id", "studentActualGraduationMonth_id"],
    ["studentGraduationYear_id", "studentActualGraduationYear_id"],
    ["studentGraduationGrade_id", "studentGraduationGrade_id"],
    ["studentGraduationProjectGrade_id", "studentGraduationProjectGrade_id"],
    ["studentEnrollSemester_id", "studentEnrollSemester_id"],
    ["studentEnrollStage_id", "studentEnrollStage_id"],
    ["ConvertLevel", "studentLevel_id"],
    ["RegistrationTypeID", "studentRegistrationType_id"],
]
