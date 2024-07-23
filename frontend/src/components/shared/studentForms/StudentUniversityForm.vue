<template>
  <div v-if="studentUniversityEdu" class="form-container">
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="studentEnrollSemester"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentUniversityEdu.studentEnrollYear_id"
          :options="translatedFormFilters.years"
          :disabled="props.isEdit || disableStatus"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="studentEnrollSemester">{{ $t("enrollmentYear") }} </label>
      </span>
      <small
        v-for="error of v$.studentUniversityEdu.studentEnrollYear_id.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="studentEnrollSemester"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentUniversityEdu.studentEnrollSemester_id"
          :options="translatedFormFilters.semesters"
          :disabled="props.isEdit || disableStatus"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="studentEnrollSemester"
          >{{ $t("enrollmentSemester") }}
        </label>
      </span>
      <small
        v-for="error of v$.studentUniversityEdu.studentEnrollSemester_id
          .$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="studentEnrollStage"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentUniversityEdu.studentEnrollStage_id"
          :options="translatedFormFilters.stages"
          :disabled="props.isEdit || disableStatus"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="studentEnrollStage">
          {{ $t("enrollmentStage") }}
        </label>
      </span>
      <small
        v-for="error of v$.studentUniversityEdu.studentEnrollStage_id.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="studentUniveristy"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentUniversityEdu.studentRegistrationType_id"
          :options="translatedFormFilters.registrationTypes"
          :disabled="true"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="registrationType">{{ $t("registrationType") }} </label>
      </span>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="studentUniveristy"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentUniversityEdu.studentUniveristy_id"
          :options="translatedFormFilters.universities"
          :disabled="props.isEdit || disableStatus"
          @change="clearFacultyId()"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="studentUniveristy">{{ $t("enrollmentUniveristy") }} </label>
      </span>
      <small
        v-for="error of v$.studentUniversityEdu.studentUniveristy_id.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2" v-if="!isExternalUni">
      <span
        class="p-float-label"
        v-tooltip.bottom="{
          value: $t('inqueryFiltersValidations.requiredUniversity'),
          disabled: Boolean(
            props.isEdit ||
              disableStatus ||
              studentUniversityEdu.studentUniveristy_id
          ),
        }"
      >
        <Dropdown
          id="studentFaculty"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentUniversityEdu.studentFaculty_id"
          :options="translatedFormFilters.faculties"
          :disabled="
            props.isEdit ||
            disableStatus ||
            !studentUniversityEdu.studentUniveristy_id
          "
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="studentFaculty">{{ $t("enrollmentFaculty") }} </label>
      </span>
      <small
        v-for="error of v$.studentUniversityEdu.studentFaculty_id.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2" v-if="isExternalUni">
      <span class="p-float-label">
        <InputText
          id="enrollmentCustomExternal"
          class="w-full"
          type="text"
          :disabled="props.isEdit || disableStatus"
          v-model="studentUniversityEdu.studentCustomUniversityFaculty"
        />
        <label for="enrollmentCustomExternal">{{
          $t("enrollmentCustomExternal")
        }}</label>
      </span>
      <small
        v-for="error of v$.studentUniversityEdu.studentCustomUniversityFaculty
          .$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="studentExpectedGraduationYear"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentUniversityEdu.studentExpectedGraduationYear_id"
          :options="translatedFormFilters.years"
          :disabled="disableStatus"
          :showClear="true"
          @change="clearMonthId()"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="studentExpectedGraduationYear"
          >{{ $t("expectedYearGraduation") }}
        </label>
      </span>
    </div>
    <div class="field mt-3 mx-2">
      <span
        class="p-float-label"
        v-tooltip.bottom="{
          value: $t('inqueryFiltersValidations.requiredExpectedGraduation'),
          disabled: Boolean(
            disableStatus ||
              studentUniversityEdu.studentExpectedGraduationYear_id
          ),
        }"
      >
        <Dropdown
          id="studentExpectedGraduationMonth"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentUniversityEdu.studentExpectedGraduationMonth_id"
          :options="translatedFormFilters.months"
          :disabled="
            disableStatus ||
            !studentUniversityEdu.studentExpectedGraduationYear_id
          "
          :showClear="true"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="studentExpectedGraduationMonth"
          >{{ $t("expectedMonthGraduation") }}
        </label>
      </span>
    </div>
  </div>
  <template v-if="props.isEdit">
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <MultiSelect
          id="imposedCourseData"
          class="w-full"
          v-model="studentImposedCoursesIds"
          :options="translatedFormFilters.imposedCourses"
          :disabled="disableStatus || isGraduate"
          :showClear="true"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="imposedCourseData">{{ $t("imposedCourseData") }} </label>
      </span>
    </div>
    <h5 v-if="studentImposedCoursesIds.length" class="mt-1 mx-3">
      {{ $t("imposedCourseStatusData") }}
    </h5>
    <div
      class="field-checkbox mt-3 mx-2"
      v-for="course of studentImposedCourses"
      :key="course.imposedCourse_id"
    >
      <Checkbox
        :id="'course' + course.imposedCourse_id"
        v-model="course.completed"
        :disabled="isGraduate"
        :binary="true"
      />
      <label :for="'course' + course.imposedCourse_id">
        {{ getImposedCourse(course.imposedCourse_id) }}
        <span v-if="course.completed">({{ t("completed") }})</span>
      </label>
    </div>
  </template>
</template>

<script setup lang="ts">
import InputText from "primevue/inputtext";
import Checkbox from "primevue/checkbox";
import Dropdown from "primevue/dropdown";
import MultiSelect from "primevue/multiselect";
import { computed, onMounted, type PropType } from "vue";
import useVuelidate from "@vuelidate/core";
import { useI18n } from "vue-i18n";
import type {
  CouncilFilters,
  StudentImposedCourse,
  StudentUniversityEdu,
  Years,
} from "@/utils/types";
import { serverTranslate } from "@/utils/filters";
import { StudentStatus, UniversityIdEnum } from "@/utils/enums";
import {
  createI18nMessage,
  maxLength,
  type MessageProps,
} from "@vuelidate/validators";

// Importing Services
const { t } = useI18n();

// Form Filters
const translatedFormFilters = computed(() => {
  return {
    years: filterCurrentYears(
      props.formFilters.years?.map((year) => ({
        ...year,
        translatedName: year.name ? serverTranslate(year.name) : t("noData"),
      })),
      true
    ),
    months: props.formFilters.months?.map((month) => ({
      ...month,
      translatedName: month.name ? serverTranslate(month.name) : t("noData"),
    })),
    semesters: props.formFilters.semesters?.map((semester) => ({
      ...semester,
      translatedName: semester.name
        ? serverTranslate(semester.name)
        : t("noData"),
    })),
    stages: props.formFilters.stages?.map((stage) => ({
      ...stage,
      translatedName: stage.name ? serverTranslate(stage.name) : t("noData"),
    })),
    registrationTypes: props.formFilters.registrationTypes?.map((type) => ({
      ...type,
      translatedName: type.name ? serverTranslate(type.name) : t("noData"),
    })),
    universities: props.formFilters.universities?.map((university) => ({
      ...university,
      translatedName: university.name
        ? serverTranslate(university.name)
        : t("noData"),
    })),
    faculties: props.formFilters.faculties
      ?.filter(
        (faculty) =>
          faculty.univ === studentUniversityEdu.value.studentUniveristy_id
      )
      .map((faculty) => ({
        ...faculty,
        translatedName: faculty.name
          ? serverTranslate(faculty.name)
          : t("noData"),
      })),
    imposedCourses: props.formFilters.imposedCourses?.map((imposedCourse) => ({
      ...imposedCourse,
      translatedName: imposedCourse.name
        ? serverTranslate(imposedCourse.name)
        : t("noData"),
    })),
  };
});

// Computed Student Data
const disableStatus = computed(() => {
  return props.studentStatusId == StudentStatus.INITIALLY_ACCEPTED;
});
const isGraduate = computed(() => {
  return props.studentStatusId == StudentStatus.GRADUATE;
});
const isExternalUni = computed(() => {
  if (props.studentUniversityEdu) {
    return (
      props.studentUniversityEdu.studentUniveristy_id ==
      UniversityIdEnum.EXTERNAL
    );
  }
  return false;
});
const studentUniversityEdu = computed({
  get: () => props.studentUniversityEdu,
  set: (value) => emit("update:studentUniversityEdu", value),
});
const studentImposedCourses = computed({
  get: () => props.studentImposedCourses,
  set: (value) => emit("update:studentImposedCourses", value),
});
const studentImposedCoursesIds = computed({
  get: () =>
    studentImposedCourses.value.map((course) =>
      Number(course.imposedCourse_id || 0)
    ),
  set: (value) => {
    let imposedValues = [];
    for (const id of value) {
      const existingImposedCourse = studentImposedCourses.value.find(
        (course) => course.imposedCourse_id === id
      );
      if (existingImposedCourse) {
        imposedValues.push(existingImposedCourse);
      } else {
        imposedValues.push({
          imposedCourse_id: id,
        });
      }
    }
    studentImposedCourses.value = imposedValues;
  },
});

// Define Component Inputs (Props)
const props = defineProps({
  isEdit: { type: Boolean, default: true },
  studentStatusId: {
    type: Number,
    default: -1,
  },
  studentUniversityEdu: {
    type: Object as PropType<StudentUniversityEdu>,
    default: null,
  },
  studentImposedCourses: {
    type: Object as PropType<StudentImposedCourse[]>,
    default: null,
  },
  formFilters: {
    type: Object as PropType<CouncilFilters>,
    default: null,
  },
});

// Define Component Outputs (Emits)
const emit = defineEmits([
  "update:studentUniversityEdu",
  "update:studentImposedCourses",
]);

// on mount functions
onMounted(async () => {
  if (props.isEdit) {
    await v$.value.$validate();
  }
});

// Component Functions
const clearMonthId = () => {
  if (studentUniversityEdu.value) {
    studentUniversityEdu.value.studentExpectedGraduationMonth_id = undefined;
  }
};

const clearFacultyId = () => {
  if (studentUniversityEdu.value) {
    studentUniversityEdu.value.studentFaculty_id = undefined;
  }
};

const getImposedCourse = (id: number | undefined) => {
  if (id) {
    const imposedCourse = translatedFormFilters.value.imposedCourses?.find(
      (course) => course.id === id
    );
    return imposedCourse ? imposedCourse.translatedName : "";
  }
  return "";
};

const filterCurrentYears = (years?: Years[] | undefined, orEqual?: boolean) => {
  if (years) {
    const currentCode = years.find((year) => year.current == 1)?.code;
    let filteredYears: Years[] = [];
    for (const year of years) {
      if (orEqual && Number(year.code) <= Number(currentCode)) {
        filteredYears.push(year);
      } else if (Number(year.code) < Number(currentCode)) {
        filteredYears.push(year);
      }
    }
    return filteredYears;
  }
  return [];
};

// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `addEditStudentValidations.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

// Custom Validators
const checkRequiredOnAdd = (value: TemplateStringsArray) => {
  if (!props.isEdit) {
    return Boolean(value);
  }
  return true;
};
const checkRequiredOnAddNonExternal = (value: TemplateStringsArray) => {
  if (!props.isEdit && !isExternalUni.value) {
    return Boolean(value);
  }
  return true;
};
const checkRequiredOnAddExternal = (value: TemplateStringsArray) => {
  if (!props.isEdit && isExternalUni.value) {
    return Boolean(value);
  }
  return true;
};

// Validation Rules
const rules = {
  studentUniversityEdu: {
    studentEnrollYear_id: {
      checkEnrollYear: withI18nMessage(checkRequiredOnAdd),
    },
    studentEnrollSemester_id: {
      checkEnrollSemester: withI18nMessage(checkRequiredOnAdd),
    },
    studentEnrollStage_id: {
      checkEnrollStage: withI18nMessage(checkRequiredOnAdd),
    },
    studentUniveristy_id: {
      checkEnrollUniversity: withI18nMessage(checkRequiredOnAdd),
    },
    studentFaculty_id: {
      checkEnrollFaculty: withI18nMessage(checkRequiredOnAddNonExternal),
    },
    studentCustomUniversityFaculty: {
      checkCustomExternal: withI18nMessage(checkRequiredOnAddExternal),
      textFieldMaxLength: withI18nMessage(maxLength(200)),
    },
  },
};

// Set up component Validation
const v$ = useVuelidate(rules, { studentUniversityEdu });
</script>

<style scoped lang="scss"></style>
