export enum Language {
  ARABIC = "ar",
  ENGLISH = "en",
}

export enum ToastTypes {
  SUCCESS = "success",
  INFO = "info",
  WARN = "warn",
  ERROR = "error",
}

export enum ConfirmDialogTypes {
  CONFIRM = "confirm",
  WARNING = "warning",
  CRITICAL = "critical",
}

export enum InfoDialogTypes {
  INFO = "info",
  ERROR = "error",
}

export enum ApplicationEnum {
  UPLOAD_CD_FILE = 1,
  INQUIRE_CD_STUDENT = 2,
  STUDENT_INFO = 3,
  MILITARY_EDUCATION = 4,
  REVIEW_GRADUATES = 5,
  GRADUATE_INFO = 6,
  TRANSFER_STUDENTS = 7,
  NUMBER_ACCEPTED_STUDENTS = 8,
  REVIEW_INITIALLY_ACCEPTED = 9,
  ACCEPTED_STUDENT_NAMES = 10,
  UNIVERSITY_STATUS_STATISTICS = 11,
  TRANSFER_STUDENTS_STATISTICS = 12,
  DEFINE_UNIVERSITIES = 13,
  DEFINE_FACULTIES = 14,
  DEFINE_CERTIFICATES = 15,
  DEFINE_CERTIFICATE_GROUPS = 16,
}

export enum RightsEnum {
  VIEW = 1,
  ADD = 2,
  EDIT = 3,
  DELETE = 4,
}

export enum CountryEnum {
  EGYPT = 1,
}

export enum GenderEnum {
  MALE = 1,
  FEMALE = 2,
}

export enum CertificateEnum {
  EGYPTIAN_GENERAL_SECONADARY = 1,
}

export enum StudentStatus {
  INITIALLY_ACCEPTED = 1,
  ACCEPTED = 2,
  FULFILLMENT = 3,
  WITHDRAWN = 4,
  REJECTED = 5,
  TRANSFERRED = 6,
  GRADUATION_APPLICANT = 7,
  GRADUATE = 8,
}

export const StudentStatusColorMapping = {
  [StudentStatus.INITIALLY_ACCEPTED]: "green",
  [StudentStatus.ACCEPTED]: "orange",
  [StudentStatus.TRANSFERRED]: "orange",
  [StudentStatus.FULFILLMENT]: "blue",
  [StudentStatus.WITHDRAWN]: "beige",
  [StudentStatus.REJECTED]: "red",
  [StudentStatus.GRADUATION_APPLICANT]: "purple",
  [StudentStatus.GRADUATE]: "purple",
};

export enum FulfillmentTypeEnum {
  SECONDARY_FULFILLMENT = 1,
  TRANSFER_FULFILLMENT = 2,
}

export enum TransactionsTypeEnum {
  TRANSFER_FACULTY = 26,
  PATH_SHIFT = 27,
}

export enum RegistrationTypeEnum {
  PRIMARY = 1,
  INCOMING_STUDENTS = 7,
  TRANSFER = 19,
}

export enum UniversityIdEnum {
  EXTERNAL = 85,
}

export enum FiltersSearchType {
  NATIONAL_ID = "nationalID",
  SEAT_NUMBER = "seatNumber",
  STUDENT_NAME = "studentName",
}

export enum MilitaryStatusType {
  PERFORMED = "performed",
  NOT_PERFORMED = "notPerformed",
}

// Global RegEx Expressions
export const IntegerPattern = new RegExp(/^\d+$/);
export const NonDigitsPattern = new RegExp(/[^\d]/g);
export const Float3DigitPattern = new RegExp(/^\d{0,3}(?:\.\d{0,3})?$/);
export const NIDPattern = new RegExp(
  /^(2|3)[0-9][0-9](0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])(01|02|03|04|11|12|13|14|15|16|17|18|19|21|22|23|24|25|26|27|28|29|31|32|33|34|35|88)\d{5}$/
);
export const SymbolsPattern = new RegExp(
  /[^\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_\s]/g
);
export const NoSymbolsPattern = new RegExp(
  /^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_\s]*$/
);
export const DateFormatPattern = new RegExp(/(19|20)\d{2}-\d{1,2}-\d{1,2}/);
export const EmailPattern = new RegExp(
  /[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?/
);
export const ArabicPattern = new RegExp(/[أ-ي]|[\u0600-\u06FF]/g);
export const PhonePattern = new RegExp(
  /^\s*(?:\+?(\d{1,3}))?([-. (]*(\d{3})[-. )]*)?((\d{3})[-. ]*(\d{2,4})(?:[-.x ]*(\d+))?)\s*$/gm
);

export const TotalEquivDegree = 410;

