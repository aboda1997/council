from django.db import models


class Governorates(models.Model):
    governorate_code = models.FloatField(primary_key=True, db_column='كود المحافظة')
    governorate_name = models.CharField(max_length=400, db_column='المحافظة')
    police_code = models.IntegerField(db_column='police_code')

    class Meta:
        db_table = 'المحافظة'
        managed = False


class EducationalAdministrations(models.Model):
    governorate_code = models.FloatField(primary_key=True, db_column='كود المحافظة')
    edu_admin_code = models.FloatField(db_column='كود الإدارة التعليمية')
    edu_admin_name = models.CharField(max_length=400, db_column='الإدارة التعليمية')

    class Meta:
        db_table = 'الادارة'
        managed = False


class StudentsBranchList(models.Model):
    branch_code = models.IntegerField(primary_key=True, db_column='branch_code_new')
    branch_name = models.CharField(max_length=100, db_column='branch_code_new_name')

    class Meta:
        db_table = 'المجموعة'
        managed = False


class StudentGenderList(models.Model):
    gender_code = models.IntegerField(primary_key=True, db_column='male')
    gender_name = models.CharField(max_length=100, db_column='male_name')

    class Meta:
        db_table = 'النوع'
        managed = False


class StudentReligionList(models.Model):
    religion_code = models.IntegerField(primary_key=True, db_column='moslem')
    religion_name = models.CharField(max_length=100, db_column='moslem_name')

    class Meta:
        db_table = 'الديانة'
        managed = False


class SchoolTypeList(models.Model):
    school_type_code = models.IntegerField(primary_key=True, db_column='type_code')
    school_type_name = models.CharField(max_length=100, db_column='type_name')
    flag = models.CharField(max_length=100)
    tolab = models.IntegerField(db_column='TOLAB')

    class Meta:
        db_table = 'school_types'
        managed = False


class ControlList(models.Model):
    control_code = models.IntegerField(primary_key=True, db_column='controol_code')
    control_name = models.CharField(max_length=100, db_column='controol')

    class Meta:
        db_table = 'controol'
        managed = False


class NationalityList(models.Model):
    nationality_code = models.IntegerField(primary_key=True, db_column='nationality')
    nationality_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'الجنسية'
        managed = False


class LanguagesList(models.Model):
    lang_code = models.IntegerField(primary_key=True, db_column='lang')
    lang_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'اللغات'
        managed = False


class SchoolCodeList(models.Model):
    school_code = models.IntegerField(primary_key=True)
    school_name = models.CharField(max_length=100, db_column='school_code_name')

    class Meta:
        db_table = 'كود_المدرسة'
        managed = False


class StageNew(models.Model):
    seating_no = models.IntegerField(primary_key=True, unique=True)
    arabic_name = models.CharField(max_length=400, blank=True, null=True)
    school_name = models.CharField(max_length=400, blank=True, null=True)
    dept_name = models.CharField(max_length=100, blank=True, null=True)
    city_name = models.CharField(max_length=400, blank=True, null=True)
    gender_id = models.IntegerField(blank=True, null=True, db_column='male')
    religion_id = models.IntegerField(blank=True, null=True, db_column='moslem')
    national_no = models.CharField(max_length=28, blank=True, null=True)
    school_type_id = models.IntegerField(blank=True, null=True, db_column='std_type')
    branch_code_new = models.IntegerField(blank=True, null=True)
    control_code = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    day = models.IntegerField(blank=True, null=True)
    moderia = models.IntegerField(blank=True, null=True)
    nationality = models.IntegerField(blank=True, null=True)
    lang_1 = models.IntegerField(blank=True, null=True)
    lang_2 = models.IntegerField(blank=True, null=True)
    dept_code = models.IntegerField(blank=True, null=True)
    police_code = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    police_station = models.CharField(max_length=200, blank=True, null=True)
    city_code = models.IntegerField(blank=True, null=True)
    birth_palace = models.CharField(max_length=200, blank=True, null=True)
    school_code = models.IntegerField(blank=True, null=True)
    arabic_deg = models.FloatField(blank=True, null=True, db_column="s1")
    lang_1_deg = models.FloatField(blank=True, null=True, db_column="s2")
    lang_2_deg = models.FloatField(blank=True, null=True, db_column="s3")
    pure_math_deg = models.FloatField(blank=True, null=True, db_column="s6")
    history_deg = models.FloatField(blank=True, null=True, db_column="s17")
    geography_deg = models.FloatField(blank=True, null=True, db_column="s8")
    philosophy_deg = models.FloatField(blank=True, null=True, db_column="s18")
    psychology_deg = models.FloatField(blank=True, null=True, db_column="s9")
    chemistry_deg = models.FloatField(blank=True, null=True, db_column="s4")
    biology_deg = models.FloatField(blank=True, null=True, db_column="s5")
    geology_deg = models.FloatField(blank=True, null=True, db_column="s7")
    applied_math_deg = models.FloatField(blank=True, null=True, db_column="s16")
    physics_deg = models.FloatField(blank=True, null=True, db_column="s15")
    total_degree = models.FloatField(blank=True, null=True)
    religious_education_deg = models.FloatField(blank=True, null=True, db_column="s10")
    national_education_deg = models.FloatField(blank=True, null=True, db_column="s14")
    economics_deg = models.FloatField(blank=True, null=True, db_column="s19")
    no_of_fail = models.IntegerField(blank=True, null=True)
    tanseq_number = models.IntegerField(blank=True, null=True)
    bar_code = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'stagenew'
        managed = False


def set_db_ref(db_name):
    StageNew.objects = StageNew.objects.using(db_name)
    SchoolCodeList.objects = SchoolCodeList.objects.using(db_name)
    LanguagesList.objects = LanguagesList.objects.using(db_name)
    NationalityList.objects = NationalityList.objects.using(db_name)
    ControlList.objects = ControlList.objects.using(db_name)
    SchoolTypeList.objects = SchoolTypeList.objects.using(db_name)
    StudentReligionList.objects = StudentReligionList.objects.using(db_name)
    StudentGenderList.objects = StudentGenderList.objects.using(db_name)
    StudentsBranchList.objects = StudentsBranchList.objects.using(db_name)
    EducationalAdministrations.objects = EducationalAdministrations.objects.using(
        db_name
    )
    Governorates.objects = Governorates.objects.using(db_name)


set_db_ref('gs_2021')
