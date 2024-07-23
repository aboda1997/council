from django.db import models
from django.utils import timezone

from core.models.base import BaseDbModel


class User(BaseDbModel):
    """
    A model that stores all system users
    """
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    fullname = models.CharField(max_length=256, blank=True)
    nid = models.BigIntegerField(default=0, null=True)
    email = models.CharField(max_length=200, null=True)

    token = models.TextField(max_length=1000, null=True)

    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'users'


class ApplicationCategory(BaseDbModel):
    """
    A model that store the various Application Categories
    """

    name = models.CharField(max_length=50, unique=True)
    displayName = models.CharField(max_length=128, default="Unnamed App")
    icon = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'applicationscategories'


class Application(BaseDbModel):
    """
    A model that store Data about each system application
    """

    name = models.CharField(max_length=50, unique=True)
    displayName = models.CharField(max_length=128, default="Unnamed App")
    icon = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(
        ApplicationCategory, on_delete=models.PROTECT, null=True
    )
    rights = models.CharField(max_length=256, null=True)

    class Meta:
        db_table = 'applications'


class Right(BaseDbModel):
    """
    A model that store Data about each possible Application Rights
    """

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'rights'


class UserAppliction(BaseDbModel):
    """
    A model that sets permission of each user and application they can use
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    right = models.ForeignKey(Right, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'userapplictions'


class Grades(BaseDbModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    type = models.CharField(max_length=11, blank=True, null=True)
    typeid = models.CharField(max_length=100)
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'grades'


class Years(BaseDbModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    current = models.IntegerField()
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'years'


class Months(BaseDbModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'months'


class Certificates(BaseDbModel):
    name = models.CharField(unique=True, max_length=50)
    code = models.CharField(unique=True, max_length=50)
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'certificates'


class Stages(BaseDbModel):
    name = models.CharField(unique=True, max_length=50)
    code = models.CharField(unique=True, max_length=50)
    current = models.BooleanField()
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'stages'


class Semesters(BaseDbModel):
    name = models.CharField(unique=True, max_length=50)
    code = models.CharField(unique=True, max_length=50)
    current = models.BooleanField()
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'semesters'


class CertificateGroup(BaseDbModel):
    name = models.CharField(max_length=255)
    year = models.ForeignKey(Years, on_delete=models.CASCADE, related_name="group_year")
    semester = models.ForeignKey(
        Semesters, on_delete=models.CASCADE, related_name="group_semester"
    )
    stage = models.ForeignKey(
        Stages, on_delete=models.CASCADE, related_name="group_stage"
    )
    sinaiResidentsReduction = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'certificategroups'


class CertificateGroupRelations(models.Model):
    createdAt = models.DateTimeField(default=timezone.now, blank=False, null=False)
    createdBy = models.IntegerField(default=0, blank=False, null=False)
    certificate = models.ForeignKey(
        Certificates, on_delete=models.CASCADE, related_name="related_certificate"
    )
    certificateGroup = models.ForeignKey(
        CertificateGroup,
        on_delete=models.CASCADE,
        related_name="related_certificate_group",
    )

    class Meta:
        db_table = 'certificategrouprelations'


class Regions(BaseDbModel):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=11, blank=True, null=True)
    typeid = models.CharField(max_length=100)
    parent = models.CharField(max_length=11, blank=True, null=True)
    gscdid = models.CharField(max_length=11, blank=True, null=True)
    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    tansiqid = models.CharField(max_length=100, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'regions'


class Universities(BaseDbModel):
    name = models.CharField(max_length=500)
    gov = models.ForeignKey(Regions, on_delete=models.CASCADE, default=17)
    typeid = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=200, blank=True, null=True)
    tansiqid = models.CharField(max_length=100, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'universities'


class StudyGroups(BaseDbModel):
    name = models.CharField(unique=True, max_length=50)
    code = models.CharField(unique=True, max_length=50)
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'studygroups'


class Sectors(BaseDbModel):
    name = models.CharField(unique=True, max_length=50)
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'sectors'


class FacultyName(BaseDbModel):
    name = models.CharField(unique=True, max_length=255)
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'facultyname'


class Faculties(BaseDbModel):
    name = models.CharField(max_length=200)
    sector = models.ForeignKey(Sectors, on_delete=models.CASCADE)
    facultyname = models.ForeignKey(FacultyName, on_delete=models.CASCADE)
    studygroup = models.ForeignKey(StudyGroups, on_delete=models.CASCADE)
    univ = models.ForeignKey(Universities, on_delete=models.CASCADE)
    facode = models.CharField(db_column='faCode', max_length=50, blank=True, null=True)
    tansiqid = models.CharField(max_length=100, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'faculties'


class Status(BaseDbModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=100)
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'status'


class RegistrationType(BaseDbModel):
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=False)
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'registrationtype'


class Level(BaseDbModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=100, blank=True, null=True)
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'level'


class Gender(BaseDbModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=100)
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'gender'


class Religion(BaseDbModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=100)
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'religion'


class SchoolType(BaseDbModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=100)
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'schooltype'


class Fulfillment(BaseDbModel):
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=100, blank=True, null=True)
    typeid = models.CharField(max_length=100)

    class Meta:
        db_table = 'fulfillment'


class ImposedCourses(BaseDbModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=100)

    class Meta:
        db_table = 'imposedcourses'


class BaseStudents(BaseDbModel):
    """
    A model that stores students basic data
    """

    studentNID = models.CharField(max_length=14, null=True)
    studentPassport = models.CharField(max_length=25, null=True)
    studentName = models.CharField(max_length=255, null=True)
    studentGender = models.ForeignKey(
        Gender, on_delete=models.CASCADE, related_name='%(class)s_gender', null=True
    )
    studentPhone = models.CharField(max_length=20, null=True)
    studentMail = models.CharField(max_length=100, null=True)
    studentAddress = models.CharField(max_length=200, null=True)
    studentNationality = models.ForeignKey(
        Regions,
        on_delete=models.CASCADE,
        related_name='%(class)s_nationality',
        null=True,
    )
    studentReligion = models.ForeignKey(
        Religion, on_delete=models.CASCADE, related_name='%(class)s_religion', null=True
    )
    studentStatus = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        related_name='%(class)s_status',
        null=True,
        default=189,
    )
    studentBirthPlaceGov = models.ForeignKey(
        Regions,
        on_delete=models.CASCADE,
        related_name='%(class)s_governorate',
        null=True,
    )
    studentAddressPlaceGov = models.ForeignKey(
        Regions,
        on_delete=models.CASCADE,
        related_name='%(class)s_add_governorate',
        null=True,
    )
    studentBirthDate = models.DateField(null=True)
    notes = models.TextField(null=True)
    migration_notes = models.TextField(null=True)
    uniqueId = models.CharField(max_length=255, blank=True, null=True)
    tansiqid = models.CharField(max_length=255, blank=True, null=True)
    oldcouncilid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True


class Students(BaseStudents):
    class Meta:
        db_table = 'students'


class Graduates(BaseStudents):
    class Meta:
        db_table = 'graduates'


class BaseSecondaryEdu(BaseDbModel):
    """
    A model that stores students basic data
    """

    student = models.ForeignKey(
        Students, on_delete=models.CASCADE, related_name='secondary'
    )
    studentSchool = models.CharField(max_length=200, null=True)
    studentSchoolType = models.ForeignKey(
        SchoolType, on_delete=models.CASCADE, related_name='%(class)s_school', null=True
    )
    studentDept = models.CharField(max_length=200, null=True)
    studentDeptCode = models.ForeignKey(
        Regions, on_delete=models.CASCADE, related_name='%(class)s_dept', null=True
    )
    studentGov = models.ForeignKey(
        Regions, on_delete=models.CASCADE, related_name='%(class)s_gov', null=True
    )
    studentSeatNumber = models.CharField(max_length=20, null=True)
    studentStudyGroup = models.ForeignKey(
        StudyGroups, on_delete=models.CASCADE, related_name='%(class)s_group', null=True
    )
    studentCertificateYear = models.ForeignKey(
        Years,
        on_delete=models.CASCADE,
        related_name='%(class)s_certificate_year',
        null=True,
    )
    studentSecondaryCert = models.ForeignKey(
        Certificates, on_delete=models.CASCADE, related_name='%(class)s_cert', null=True
    )
    studentTot = models.CharField(max_length=10, null=True)
    studentEquivTot = models.CharField(max_length=10, null=True)
    studentSportDegree = models.CharField(max_length=10, null=True)
    studentComplainGain = models.CharField(max_length=10, null=True)
    studentFulfillment = models.ForeignKey(
        Fulfillment,
        on_delete=models.CASCADE,
        related_name='%(class)s_fulfillment',
        null=True,
    )

    class Meta:
        abstract = True


class StudentsSecondaryEdu(BaseSecondaryEdu):
    class Meta:
        db_table = 'studentssecondaryedu'


class GraduatesSecondaryEdu(BaseSecondaryEdu):
    student = models.ForeignKey(
        Graduates, on_delete=models.CASCADE, related_name='secondary'
    )

    class Meta:
        db_table = 'graduatessecondaryedu'


class BaseUniversityEdu(BaseDbModel):
    student = models.ForeignKey(
        Students, on_delete=models.CASCADE, related_name='university'
    )
    studentFaculty = models.ForeignKey(
        Faculties, on_delete=models.CASCADE, related_name='%(class)s_faculty', null=True
    )
    studentUniveristy = models.ForeignKey(
        Universities,
        on_delete=models.CASCADE,
        related_name='%(class)s_university',
        null=True,
    )
    studentCustomUniversityFaculty = models.CharField(max_length=200, null=True)
    studentEnrollSemester = models.ForeignKey(
        Semesters,
        on_delete=models.CASCADE,
        related_name='%(class)s_semester',
        null=True,
    )
    studentEnrollStage = models.ForeignKey(
        Stages, on_delete=models.CASCADE, related_name='%(class)s_stage', null=True
    )
    studentEnrollYear = models.ForeignKey(
        Years, on_delete=models.CASCADE, related_name='%(class)s_enroll_year', null=True
    )
    studentTot = models.CharField(max_length=20, null=True)
    studentExpectedGraduationYear = models.ForeignKey(
        Years,
        on_delete=models.CASCADE,
        related_name='%(class)s_expected_graduation_year',
        null=True,
    )
    studentExpectedGraduationMonth = models.ForeignKey(
        Months,
        on_delete=models.CASCADE,
        related_name='%(class)s_expected_graduation_month',
        null=True,
    )
    studentActualGraduationYear = models.ForeignKey(
        Years,
        on_delete=models.CASCADE,
        related_name='%(class)s_actual_graduation_year',
        null=True,
    )
    studentActualGraduationMonth = models.ForeignKey(
        Months,
        on_delete=models.CASCADE,
        related_name='%(class)s_actual_graduation_month',
        null=True,
    )
    studentSpecialization = models.CharField(max_length=100, null=True)
    studentDivision = models.CharField(max_length=100, null=True)
    studentGraduationGrade = models.ForeignKey(
        Grades,
        on_delete=models.CASCADE,
        related_name='%(class)s_graduation_grade',
        null=True,
    )
    studentGraduationPercentage = models.CharField(max_length=20, null=True)
    studentGraduationGPA = models.CharField(max_length=20, null=True)
    studentGraduationEquivalentHours = models.CharField(max_length=20, null=True)
    studentGraduationProjectGrade = models.ForeignKey(
        Grades,
        on_delete=models.CASCADE,
        related_name='%(class)s_graduation_project_grade',
        null=True,
    )
    studentRegistrationType = models.ForeignKey(
        RegistrationType,
        on_delete=models.CASCADE,
        related_name='%(class)s_registration_type',
        null=True,
    )
    studentLevel = models.ForeignKey(
        Level,
        on_delete=models.CASCADE,
        related_name='%(class)s_level',
        null=True,
    )
    totalEquivalentHours = models.CharField(max_length=20, null=True)
    transferDate = models.DateField(null=True)
    transferFulfillment = models.ForeignKey(
        Fulfillment,
        on_delete=models.CASCADE,
        related_name='%(class)s_fulfillment',
        null=True,
    )
    pathShiftDate = models.DateField(null=True)

    class Meta:
        abstract = True


class StudentsUniversityEdu(BaseUniversityEdu):
    class Meta:
        db_table = 'studentsuniversityedu'


class GraduatesUniversityEdu(BaseUniversityEdu):
    student = models.ForeignKey(
        Graduates, on_delete=models.CASCADE, related_name='university'
    )

    class Meta:
        db_table = 'graduatesuniversityedu'


class BaseImposedCourses(BaseDbModel):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    imposedCourse = models.ForeignKey(
        ImposedCourses,
        on_delete=models.CASCADE,
        related_name='%(class)s_imposed_course',
    )
    completed = models.BooleanField(default=False)

    class Meta:
        abstract = True


class StudentsImposedCourses(BaseImposedCourses):
    class Meta:
        db_table = 'studentsimposedcourses'


class GraduatesImposedCourses(BaseImposedCourses):
    student = models.ForeignKey(Graduates, on_delete=models.CASCADE)

    class Meta:
        db_table = 'graduatesimposedcourses'


class BaseMilitaryEdu(BaseDbModel):
    student = models.ForeignKey(
        Students, on_delete=models.CASCADE, related_name='military'
    )
    militaryEduYear = models.ForeignKey(
        Years,
        on_delete=models.CASCADE,
        related_name='%(class)s_year',
        null=True,
    )
    militaryEduMonth = models.ForeignKey(
        Months,
        on_delete=models.CASCADE,
        related_name='%(class)s_month',
        null=True,
    )
    militaryEduGrade = models.ForeignKey(
        Grades,
        on_delete=models.CASCADE,
        related_name='%(class)s_grade',
        null=True,
    )

    class Meta:
        abstract = True


class StudentsMilitaryEdu(BaseMilitaryEdu):
    class Meta:
        db_table = 'studentsmilitaryedu'


class GraduatesMilitaryEdu(BaseMilitaryEdu):
    student = models.ForeignKey(
        Graduates, on_delete=models.CASCADE, related_name='military'
    )

    class Meta:
        db_table = 'graduatesmilitaryedu'


class StudentsAcceptedApplication(BaseDbModel):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    fac = models.ForeignKey(Faculties, on_delete=models.CASCADE, null=True)
    year = models.ForeignKey(
        Years, on_delete=models.CASCADE, related_name='appacc_year', default=57
    )
    semester = models.ForeignKey(
        Semesters, on_delete=models.CASCADE, related_name='appacc_smester', default=56
    )
    stage = models.ForeignKey(
        Stages, on_delete=models.CASCADE, related_name='appacc_stage', default=29
    )
    studentTot = models.CharField(max_length=200, null=True)
    manualAddition = models.CharField(max_length=200, default=0)

    class Meta:
        db_table = 'studentsacceptedapplication'


class TransactionsType(BaseDbModel):
    name = models.CharField(max_length=200)

    class Meta:
        db_table = "transactionstype"


class StudentsTransactions(models.Model):
    createdAt = models.DateTimeField(default=timezone.now, blank=False, null=False)
    createdBy = models.IntegerField(default=0, blank=False, null=False)

    uniqueId = models.CharField(max_length=255, blank=False, null=False)
    transactionType = models.ForeignKey(
        TransactionsType, on_delete=models.CASCADE, related_name="transaction_type"
    )
    message = models.CharField(max_length=255, null=True)
    originalData = models.CharField(max_length=255, null=True)
    updatedData = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "studentstransactions"


class FacultyProfiles(BaseDbModel):
    faculty = models.ForeignKey(
        Faculties, on_delete=models.CASCADE, related_name="profile_faculty"
    )
    year = models.ForeignKey(
        Years, on_delete=models.CASCADE, related_name="profile_year"
    )
    semester = models.ForeignKey(
        Semesters, on_delete=models.CASCADE, related_name="profile_semester"
    )
    stage = models.ForeignKey(
        Stages, on_delete=models.CASCADE, related_name="profile_stage"
    )

    class Meta:
        db_table = "facultyprofiles"


class FacultySeatsProfiles(BaseDbModel):
    facultyProfile = models.ForeignKey(
        FacultyProfiles, on_delete=models.CASCADE, related_name="seats_profile_parent"
    )
    registrationType = models.ForeignKey(
        RegistrationType,
        on_delete=models.CASCADE,
        related_name="seats_profile_reg_type",
    )
    certificateGroup = models.ForeignKey(
        CertificateGroup,
        on_delete=models.CASCADE,
        related_name="seats_profile_cert_group",
        blank=True,
        null=True,
    )
    seats = models.IntegerField()

    class Meta:
        db_table = "facultyseatsprofiles"


class FacultyCertProfiles(BaseDbModel):
    facultyProfile = models.ForeignKey(
        FacultyProfiles, on_delete=models.CASCADE, related_name="cert_profile_parent"
    )
    certificate = models.ForeignKey(
        Certificates, on_delete=models.CASCADE, related_name="cert_profile_cert"
    )
    certificateYear = models.ForeignKey(
        Years, on_delete=models.CASCADE, related_name="cert_profile_cert_year"
    )
    certificateGroup = models.ForeignKey(
        CertificateGroup,
        on_delete=models.CASCADE,
        related_name="cert_profile_cert_group",
    )
    minimumDegree = models.FloatField()

    class Meta:
        db_table = "facultycertprofiles"


class StudentsAttachments(models.Model):
    createdAt = models.DateTimeField(default=timezone.now, blank=False, null=False)
    createdBy = models.IntegerField(default=0, blank=False, null=False)

    uniqueId = models.CharField(max_length=255, blank=False, null=False)

    attachmentId = models.CharField(max_length=50, null=True)
    filename = models.CharField(max_length=500, null=True)
    mimetype = models.CharField(max_length=30, null=True)

    class Meta:
        db_table = "studentsattachments"
