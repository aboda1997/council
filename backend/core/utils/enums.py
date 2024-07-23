from enum import Enum


class TokenType(Enum):
    ACCESS_TOKEN = 0
    REFRESH_TOKEN = 1
    RESET_TOKEN = 2


class RightEnum(Enum):
    VIEW = 1
    SAVE = 2
    EDIT = 3
    DELETE = 4


class ApplicationCategoryEnum(Enum):
    SUPERVISION = 1
    STUDENTS = 2


class ApplicationEnum(Enum):
    UPLOAD_CD_FILE = 1
    INQUIRE_CD_STUDENT = 2
    STUDENT_INFO = 3
    MILITARY_EDUCATION = 4
    REVIEW_GRADUATES = 5
    INQUIRE_GRADUATE_INFO = 6
    TRANSFER_STUDENTS = 7
    NUMBER_ACCEPTED_STUDENTS = 8
    REVIEW_INITIALLY_ACCEPTED = 9
    ACCEPTED_STUDENT_NAMES = 10
    UNIVERSITY_STATUS_STATISTICS = 11
    TRANSFER_STUDENTS_STATISTICS = 12
    DEFINE_UNIVERSITIES = 13
    DEFINE_FACULTIES = 14
    DEFINE_CERTIFICATES = 15
    DEFINE_CERTIFICATE_GROUPS = 16


class ServiceEnum(Enum):
    INITIALLY_ACCEPTED_STUDENTS = 1


class GenderEnum(Enum):
    MALE = 1
    FEMALE = 2


class CertificateEnum(Enum):
    EGYPTIAN_GENERAL_SECONADARY = 1


class CountryEnum(Enum):
    EGYPT = 1


class RegionType(Enum):
    COUNTRY = 1
    GOVERNORATE = 2
    ADMINISTRATION = 3


class StageEnum(Enum):
    FIRST = 1
    SECOND = 2


class SemesterEnum(Enum):
    FIRST = 1
    SECOND = 2


class UniversityTypeEnum(Enum):
    COUNCIL = 1
    PRIVATE = 2
    COMMUNITY1 = 3
    COMMUNITY2 = 4
    COMMUNITY3 = 5
    CONVENTION = 6
    GOVERNMENTAL = 7
    INSTITUTE = 8
    EXTERNAL = 9
    PRIVATE_NATIONAL = [PRIVATE, COMMUNITY1, COMMUNITY2, COMMUNITY3, CONVENTION]
    NON_PRIVATE_NATIONAL = [COUNCIL, GOVERNMENTAL, INSTITUTE, EXTERNAL]


class UniversityIdEnum(Enum):
    EXTERNAL = 85


class GradeEnum(Enum):
    FAIL = 7
    F = 22
    FAILING_GRADES = [FAIL, F]


class StudentStatus(Enum):
    INITIALLY_ACCEPTED = 1
    ACCEPTED = 2
    FULFILLMENT = 3
    WITHDRAWN = 4
    REJECTED = 5
    TRANSFERRED = 6
    GRADUATION_APPLICANT = 7
    GRADUATE = 8
    ACCEPTANCE_STATUS = [ACCEPTED, FULFILLMENT]


class MilitaryStatusType(Enum):
    PERFORMED = "performed"
    NOT_PERFORMED = "notPerformed"


class TransactionsTypeEnum(Enum):
    ADDED_FROM_TANSIQ = 2
    WITHDRAW_BY_TANSIQ = 3
    NAME_CHANGE = 4
    NID_CHANGE = 5
    SEC_TOTAL_CHANGE = 6
    SEC_EQV_TOTAL_CHANGE = 7
    SEC_CERT_CHANGE = 8
    SEC_CERT_YEAR_CHANGE = 9
    GRADUATION_YEAR_CHANGE = 10
    GRADUATION_MONTH_CHANGE = 11
    GRADUATION_GPA_CHANGE = 15
    GRADUATION_GRADE_CHANGE = 16
    IMPOSED_COURSES_CHANGE = 17
    MILITARY_EDU_CHANGE = 18
    CHANGE_TO_ACCEPTED = 20
    CHANGE_TO_FULFILLMENT = 21
    CHANGE_TO_WITHDRAWN = 22
    CHANGE_TO_REJECTED = 23
    TRANSFER_FACULTY = 26
    PATH_SHIFT = 27
    MANUALLY_ADDED = 28
    WITHDRAW_BY_OLD_COUNCIL = 29
    DATA_FROM_OLD_SYSTEM = 30
    REVERT_STUDENT_DATA = 31


class RegistrationTypeEnum(Enum):
    PRIMARY = 1
    INCOMING_STUDENTS = 7
    TRANSFER = 19


# Global RegEx Expressions
IntegerPattern = r"^\d+$"
FloatPattern = r"^\d{0,3}(?:\.\d{0,3})?$"
NIDPattern = r"^(2|3)[0-9][0-9](0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])(01|02|03|04|11|12|13|14|15|16|17|18|19|21|22|23|24|25|26|27|28|29|31|32|33|34|35|88)\d{5}$"
NoSymbolsPattern = r"^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_|\s]*$"
DisallowedCharactersPattern = r"[^\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_|\s]*"
DisallowedExtraSpacesPattern = r"^\s+|\s(?=\s+)|\s+$"
DateFormatPattern = r"^(18|19|20)\d{2}-\d{1,2}-\d{1,2}$"
EmailPattern = r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
PhonePattern = r"^\s*(?:\+?(\d{1,3}))?([-. (]*(\d{3})[-. )]*)?((\d{3})[-. ]*(\d{2,4})(?:[-.x ]*(\d+))?)\s*$"
TotalDegreePattern = r"^(|(\d{1,3})?(\.\d{1,3})?)$"
ISODatePattern = r"^(19|20)\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])"
