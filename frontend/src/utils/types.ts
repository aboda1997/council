import type { FiltersSearchType } from "./enums";

export interface UserModel {
  username?: string;
  fullname?: string;
  nid?: number;
  email?: string;
}

export interface AppCategory {
  id: number;
  name: string;
  icon: string;
  displayName: string;
}

export interface UserApplication {
  id: number;
  name: string;
  icon: string;
  displayName: string;
  categoryId: number;
  rights: number[];
}

export interface UserPermissions {
  appCategories: AppCategory[];
  userApplications: UserApplication[];
}

export interface Signature {
  signatureId?: number;
  signatureName?: string;
  signatureDate?: string;
}

export interface TableColumn {
  header?: string;
  field?: string;
  sortable?: boolean;
  statusIdField?: string;
  prefix?: string | (() => string);
  suffix?: string | (() => string);
}

export interface BasicAttribute {
  id?: number;
  name?: string;
  code?: string;
  current?: number;
  translatedName?: string;
}

export interface Faculty {
  id: number | string;
  name: string;
  sector: number;
  facultyname: number;
  studygroup: number;
  univ: number;
  facode: string;
}

export interface Region {
  id: number;
  name: string;
  type: string;
  typeid: string;
  parent: string;
  gscdid: string;
}

export interface Certificate {
  id: number;
  name: string;
  code: string;
}

export interface Region {
  id: number;
  name: string;
  type: string;
  typeid: string;
  parent: string;
  gscdid: string;
}

export interface University {
  id: number;
  name: string;
  type: string;
  typeid: string;
  parent: string;
  gscdid: string;
}

export interface StudyGroup {
  id: number;
  name: string;
  code: number;
}

export interface Sector {
  id: number;
  name: string;
}

export interface FacultiesName {
  id: number;
  name: string;
}

export interface Status {
  id: number;
  name: string;
  code: string;
}

export interface Stages {
  id: number;
  name: string;
  code: string;
}

export interface Years {
  id: number;
  name: string;
  code: string;
  current: number;
}

export interface Grade {
  id: number;
  name: string;
  code: string;
  type: string;
  typeid: string;
}

export interface Semesters {
  id: number;
  name: string;
  code: string;
}

export interface Level {
  id: number;
  name: string;
}
export interface RegistrationType {
  id: number;
  name: string;
  active: boolean;
}
export interface Fulfillment {
  id: number;
  name: string;
  typeid: string;
  type: string;
}

export interface CouncilFilters {
  years?: Years[];
  certificates?: Certificate[];
  stages?: Stages[];
  semesters?: Semesters[];
  religions?: BasicAttribute[];
  countries?: Region[];
  genders?: BasicAttribute[];
  governorates?: Region[];
  adminstrations?: Region[];
  universities?: University[];
  studyGroups?: StudyGroup[];
  sectors?: Sector[];
  faculties?: Faculty[];
  facultiesNames?: FacultiesName[];
  status?: Status[];
  months?: BasicAttribute[];
  fulfillments?: Fulfillment[];
  imposedCourses?: BasicAttribute[];
  universityYear?: Years[];
  gsYear?: Years[];
  grades?: BasicAttribute[];
  acedemicGrades?: BasicAttribute[];
  levels?: Level[];
  registrationTypes?: RegistrationType[];
}

export interface GSFilters {
  governorates?: {
    governorate_code: number;
    governorate_name: string;
    police_code: number;
  }[];
  educationalAdministrations?: {
    governorate_code: number;
    edu_admin_code: number;
    edu_admin_name: string;
  }[];
  studentsBranchList?: {
    branch_code: number;
    branch_code_str: string;
    branch_name: string;
  }[];
  studentGenderList?: {
    gender_code: number;
    gender_name: string;
  }[];
  studentReligionList?: {
    religion_code: number;
    religion_name: string;
  }[];
  schoolTypeList?: {
    school_type_code: number;
    school_type_name: string;
    flag: string;
    tolab: number;
  }[];
  controlList?: {
    control_code: number;
    control_name: string;
  }[];
  nationalityList?: {
    nationality_code: number;
    nationality_name: string;
  }[];
  languagesList?: {
    lang_code: number;
    lang_code_str: string;
    lang_name: string;
  }[];
  schoolCodeList?: {
    school_code: number;
    school_name: string;
  }[];
}

export interface Student {
  id?: number;
  studentNID?: number;
  studentPassport?: string;
  studentName?: string;
  studentPhone?: string;
  studentMail?: string;
  studentAddress?: string;
  studentBirthDate?: string;
  studentGender_id?: number;
  studentGender__name?: string;
  studentAddressPlaceGov_id?: number;
  studentAddressPlaceGov__name?: string;
  studentBirthPlaceGov_id?: number;
  studentBirthPlaceGov__name?: string;
  studentNationality_id?: number;
  studentNationality__name?: string;
  studentReligion_id?: number;
  studentReligion__name?: string;
  studentStatus_id?: number;
  studentStatus__name?: string;
  uniqueId?: string;
  withdrawalDate?: string;
  notes?: string;
}

export interface StudentSecondaryEdu {
  id?: number;
  studentSchool?: string;
  studentDept?: string;
  studentSeatNumber?: number;
  studentTot?: number;
  studentEquivTot?: number;
  studentTotPrecentage?: number;
  studentSportDegree?: number;
  studentComplainGain?: number;
  studentCertificateYear_id?: number;
  studentCertificateYear__name?: string;
  studentDeptCode_id?: number;
  studentGov_id?: number;
  studentGov__name?: string;
  studentSchoolType_id?: number;
  studentSchoolType__name?: number;
  studentSecondaryCert_id?: number;
  studentSecondaryCert__name?: string;
  studentStudyGroup_id?: number;
  studentStudyGroup__name?: string;
  studentFulfillment_id?: number;
  studentFulfillment__name?: string;
}

export interface StudentUniversityEdu {
  id?: number;
  studentExpectedGraduationYear_id?: string;
  studentExpectedGraduationYear__name?: string;
  studentExpectedGraduationMonth_id?: string;
  studentExpectedGraduationMonth__name?: string;
  studentEnrollSemester_id?: number;
  studentEnrollSemester__name?: string;
  studentEnrollStage_id?: number;
  studentEnrollStage__name?: string;
  studentEnrollYear_id?: number;
  studentEnrollYear__name?: string;
  studentCustomUniversityFaculty?: string;
  studentRegistrationType_id?: number;
  studentRegistrationType__name?: string;
  studentFaculty_id?: number;
  studentFaculty__name?: string;
  studentUniveristy_id?: number;
  studentUniveristy__name?: string;
  studentGraduationGPA?: number;
  studentGraduationGrade_id?: number;
  studentGraduationGrade__name?: string;
  studentGraduationPercentage?: number;
  studentGraduationEquivalentHours?: number;
  studentSpecialization?: string;
  studentDivision?: string;
  studentGraduationProjectGrade_id?: number;
  studentGraduationProjectGrade__name?: string;
  studentActualGraduationYear_id?: number;
  studentActualGraduationYear__name?: string;
  studentActualGraduationMonth_id?: number;
  studentActualGraduationMonth__name?: string;
  studentLevel_id?: number;
  studentLevel__name?: string;
  totalEquivalentHours?: number;
  transferDate?: string;
  transferFulfillment_id?: number;
  transferFulfillment__name?: number;
  studentPrevUniveristy_id?: number;
  studentPrevUniveristy__name?: string;
  studentPrevFaculty_id?: number;
  studentPrevFaculty__name?: string;
  studentPrevEnrollYear_id?: number;
  studentPrevEnrollYear__name?: string;
  studentPrevEnrollSemester_id?: string;
  studentPrevEnrollSemester__name?: string;
  studentPrevEnrollStage_id?: string;
  studentPrevEnrollStage__name?: string;
  studentPrevCustomUniversityFaculty?: string;
  studentTot?: number;
}

export interface StudentMilitaryEdu {
  id?: number;
  student_id?: number;
  student__studentName?: string;
  militaryEduYear_id?: number;
  militaryEduYear__name?: string;
  militaryEduMonth_id?: number;
  militaryEduMonth__name?: string;
  militaryEduGrade_id?: number;
  militaryEduGrade__name?: string;
  militaryEduPerform?: string;
  isApplicable?: boolean;
}

export interface StudentImposedCourse {
  student_id?: number;
  imposedCourse_id?: number;
  imposedCourse__name?: string;
  completed?: boolean;
}

export interface StudentTransaction {
  id?: number;
  createdAt?: string;
  createdBy?: string;
  transactionType_id?: number;
  transactionType__name?: string;
  transactionChanges?: {
    from: string;
    to: string;
  }[];
  icon?: string;
}

export interface CDStudent {
  seating_no?: number;
  arabic_name?: string;
  school_name?: string;
  dept_name?: string;
  city_name?: string;
  gender_id?: number;
  religion_id?: number;
  national_no?: string;
  school_type_id?: number;
  branch_code_new?: number | string;
  control_code?: number;
  year?: number;
  month?: number;
  day?: number;
  date_of_birth?: string;
  moderia?: number;
  nationality?: number;
  lang_1?: number | string;
  lang_2?: number | string;
  dept_code?: number;
  police_code?: number;
  address?: string;
  police_station?: string;
  city_code?: number;
  birth_palace?: string;
  school_code?: number | string;
  arabic_deg?: number;
  lang_1_deg?: number;
  lang_2_deg?: number;
  pure_math_deg?: number;
  history_deg?: number;
  geography_deg?: number;
  philosophy_deg?: number;
  psychology_deg?: number;
  chemistry_deg?: number;
  biology_deg?: number;
  geology_deg?: number;
  applied_math_deg?: number;
  physics_deg?: number;
  total_degree?: number;
  religious_education_deg?: number;
  national_education_deg?: number;
  economics_deg?: number;
  no_of_fail?: number;
  tanseq_number?: number;
  bar_code?: string;
  branch_name?: string;
  gender_name?: string;
  religion_name?: string;
  school_type_name?: string;
  school_code_name?: string;
  control_name?: string;
  governorate_name?: string;
  nationality_name?: string;
  first_lang_name?: string;
  second_lang_name?: string;
  cert_year?: string;
}

export interface StudentData {
  student: Student;
  studentSecondaryEdu?: StudentSecondaryEdu;
  studentUniversityEdu?: StudentUniversityEdu;
  studentImposedCourses?: StudentImposedCourse[];
  studentDegreePercentage?: number;
  attachments?: UploadedFile[];
}

export interface StudentListing {
  id?: number;
  studentNID?: string;
  studentName?: string;
  studentNationality__name?: string;
  secondary__studentSecondaryCert__name?: string;
  secondary__studentCertificateYear__name?: string;
  university__studentUniveristy__name?: string;
  university__studentFaculty__name?: string;
  university__studentTot?: string;
  university__studentGraduationGPA?: string;
  studentStatus_id?: string;
  studentStatus__name?: string;
  military__militaryEduYear_id?: number;
}

export interface InquireCDStudentQuery {
  selectedYear: string;
  searchType?: FiltersSearchType;
  search: string;
  page?: number;
  perPage?: number;
}

export interface ReportStudentsQuery {
  year?: string;
  university?: string;
  registrationTypes?: string | string[];
  semester?: string;
  stage?: string;
  studentStatus?: string;
  fulfillment?: string;
  region?: string;
  certificate?: string;
  gsYear?: string;
  registrationType?: string;
}

export interface InquireStudentQuery {
  selectedStudentType?: string;
  certificate?: string;
  faculty?: string;
  nationalID?: string;
  passport?: string;
  region?: string;
  seatNumber?: string;
  semester?: string;
  stage?: string;
  studentName?: string;
  university?: string;
  universityYear?: string;
  gsYear?: string;
  studentStatus?: string;
  page?: number;
  perPage?: number;
}

export interface TransferToFacultyReport {
  can_transfer?: boolean;
  allowed_transfer_count?: number;
  transferred_students_count?: number;
  available_transfer_count?: number;
}

export interface UploadedFile {
  filename: string;
  attachmentId?: string;
  mimetype?: string;
  size?: number;
  message?: string;
}

export interface ReportTableColumn {
  id: number;
  name: string;
}

export interface NumberAcceptedStudentsColumn {
  id: number;
  name: string;
}

export interface NumberAcceptedStudentsData {
  univ_id: string;
  univ_name: string;
  [id: string]: string;
}

export interface AcceptedStudentsNamesData {
  [id: string]: string;
}

export interface UniversityStatusStatisticsData {
  fac_type_id: string;
  fac_type_name: string;
  allocated_seats: string;
  remaining: string;
  [id: string]: string;
}

export interface GeneralResponse {
  detail: string;
}

export interface LoginResponse extends GeneralResponse {
  payload: {
    accessToken: string;
    userData: UserModel;
    userPermissions: UserPermissions;
  };
}

export interface UserPermissionsResponse extends GeneralResponse {
  payload: {
    userPermissions: UserPermissions;
  };
}

export interface ForgetPasswordResponse extends GeneralResponse {
  payload: {
    toUserEmail: string;
  };
}

export interface CheckTokenResponse extends GeneralResponse {
  payload: {
    tokenStatus: string;
  };
}

export interface CDStudentResponse extends GeneralResponse {
  payload: {
    student: CDStudent;
  };
}

export interface StudentResponse extends GeneralResponse {
  payload: {
    student: Student;
  };
}

export interface StudentsListResponse extends GeneralResponse {
  payload: {
    studentsList: CDStudent[];
    totalRecords: number;
  };
}

export interface InquireStudentsListResponse extends GeneralResponse {
  payload: {
    studentsList: StudentListing[];
    totalRecords: number;
  };
}

export interface RevertTransactionResponse extends GeneralResponse {
  payload: {
    studentUniversityEdu: StudentUniversityEdu;
  };
}

export interface MilitaryEducationListResponse extends GeneralResponse {
  payload: {
    studentsList: StudentListing[];
    totalRecords: number;
  };
}

export interface AcceptedStudentsNamesResponse extends GeneralResponse {
  payload: {
    columns: string[];
    reportData: AcceptedStudentsNamesData[];
  };
}

export interface NumberAcceptedStudentsResponse extends GeneralResponse {
  payload: {
    columns: ReportTableColumn[];
    reportData: NumberAcceptedStudentsData[];
  };
}

export interface UniversityStatusStatisticsResponse extends GeneralResponse {
  payload: {
    columns: ReportTableColumn[];
    reportData: UniversityStatusStatisticsData[];
  };
}

export interface CouncilFiltersResponse extends GeneralResponse {
  payload: CouncilFilters;
}

export interface GSListResponse extends GeneralResponse {
  payload: GSFilters;
}

export interface SecondaryGSInfo {
  student?: Student;
  studentSecondaryEdu?: StudentSecondaryEdu;
}

export interface SecondaryGSInfoResponse extends GeneralResponse {
  payload: SecondaryGSInfo;
}

export interface StudentViewPayload {
  student: Student;
  studentSecondaryEdu: StudentSecondaryEdu;
  studentUniversityEdu: StudentUniversityEdu;
  studentImposedCourses: StudentImposedCourse[];
  studentMilitaryEdu: StudentMilitaryEdu;
  signature: Signature;
  attachments?: UploadedFile[];
}
export interface StudentViewResponse extends GeneralResponse {
  payload: StudentViewPayload;
}

export interface StudentHistoryResponse extends GeneralResponse {
  payload: {
    student: Student;
    transactions: StudentTransaction[];
  };
}

export interface MilitaryEduViewResponse extends GeneralResponse {
  payload: {
    studentMilitaryEdu: StudentMilitaryEdu;
    signature: Signature;
  };
}

export interface TransferToFacultyResponse extends GeneralResponse {
  payload: TransferToFacultyReport;
}

export type DialogCallback = (hasConfirm: boolean) => void;

export interface FileActionResponse extends GeneralResponse {
  payload: {
    success: Array<UploadedFile>;
    failed: Array<UploadedFile>;
  };
}
