<template>
  <PageLoader
    v-if="isLoading || errorMessage"
    :loading="isLoading"
    :error="errorMessage"
  />
  <template v-else>
    <div class="form-container">
      <div class="field mt-3 mx-2">
        <span class="p-float-label">
          <InputNumber
            id="graduationGPA"
            class="w-full"
            type="text"
            :useGrouping="false"
            :minFractionDigits="0"
            :maxFractionDigits="3"
            :min="0"
            :max="4"
            v-model="studentUniversityEdu.studentGraduationGPA"
          />
          <label for="graduationGPA">{{ $t("graduationGPA") }}</label>
        </span>
        <small
          v-for="error of v$.studentUniversityEdu.studentGraduationGPA.$errors"
          :key="error.$uid"
          class="p-error"
        >
          {{ error.$message }} <br />
        </small>
      </div>
      <div class="field mt-3 mx-2">
        <span class="p-float-label">
          <Dropdown
            id="graduationGrade"
            class="w-full"
            v-model="studentUniversityEdu.studentGraduationGrade_id"
            :options="translatedFormFilters.grades"
            :showClear="true"
            :filter="true"
            :filterFields="['translatedName', 'name']"
            optionLabel="translatedName"
            optionValue="id"
          />
          <label for="graduationGrade">{{ $t("graduationGrade") }}</label>
        </span>
      </div>
      <div class="field mt-3 mx-2">
        <span class="p-float-label">
          <InputNumber
            id="graduationPercentage"
            class="w-full"
            type="text"
            :useGrouping="false"
            :minFractionDigits="0"
            :maxFractionDigits="3"
            v-model="studentUniversityEdu.studentGraduationPercentage"
          />
          <label for="graduationPercentage">{{
            $t("graduationPercentage")
          }}</label>
        </span>
        <small
          v-for="error of v$.studentUniversityEdu.studentGraduationPercentage
            .$errors"
          :key="error.$uid"
          class="p-error"
        >
          {{ error.$message }} <br />
        </small>
      </div>
      <div class="field mt-3 mx-2">
        <span class="p-float-label">
          <InputNumber
            id="totalEquivHours"
            class="w-full"
            type="text"
            :useGrouping="false"
            :minFractionDigits="0"
            :maxFractionDigits="3"
            v-model="studentUniversityEdu.studentGraduationEquivalentHours"
          />
          <label for="totalEquivHours">{{ $t("totalEquivHours") }}</label>
        </span>
        <small
          v-for="error of v$.studentUniversityEdu
            .studentGraduationEquivalentHours.$errors"
          :key="error.$uid"
          class="p-error"
        >
          {{ error.$message }} <br />
        </small>
      </div>
      <div class="field mt-3 mx-2">
        <span class="p-float-label">
          <InputText
            id="enrollmentSpecialization"
            class="w-full"
            type="text"
            v-model="studentUniversityEdu.studentSpecialization"
          />
          <label for="enrollmentSpecialization">{{
            $t("enrollmentSpecialization")
          }}</label>
        </span>
        <small
          v-for="error of v$.studentUniversityEdu.studentSpecialization.$errors"
          :key="error.$uid"
          class="p-error"
        >
          {{ error.$message }} <br />
        </small>
      </div>
      <div class="field mt-3 mx-2">
        <span class="p-float-label">
          <InputText
            id="enrollmentDivision"
            class="w-full"
            type="text"
            v-model="studentUniversityEdu.studentDivision"
          />
          <label for="enrollmentDivision">{{ $t("enrollmentDivision") }}</label>
        </span>
        <small
          v-for="error of v$.studentUniversityEdu.studentDivision.$errors"
          :key="error.$uid"
          class="p-error"
        >
          {{ error.$message }} <br />
        </small>
      </div>

      <div class="field mt-3 mx-2">
        <span class="p-float-label">
          <Dropdown
            id="graduationProjectGrade"
            class="w-full"
            v-model="studentUniversityEdu.studentGraduationProjectGrade_id"
            :options="translatedFormFilters.grades"
            :showClear="true"
            :filter="true"
            :filterFields="['translatedName', 'name']"
            optionLabel="translatedName"
            optionValue="id"
          />
          <label for="graduationProjectGrade"
            >{{ $t("graduationProjectGrade") }}
          </label>
        </span>
      </div>
      <div class="field mt-3 mx-2">
        <span class="p-float-label">
          <Dropdown
            id="studentActualGraduationYear"
            class="w-full"
            v-model="studentUniversityEdu.studentActualGraduationYear_id"
            :options="translatedFormFilters.years"
            :filter="true"
            :filterFields="['translatedName', 'name']"
            @change="clearMonthId()"
            optionLabel="translatedName"
            optionValue="id"
          />
          <label for="studentActualGraduationYear"
            >{{ $t("actualYearGraduation") }}
          </label>
        </span>
        <small
          v-for="error of v$.studentUniversityEdu.studentActualGraduationYear_id
            .$errors"
          :key="error.$uid"
          class="p-error"
        >
          {{ error.$message }} <br />
        </small>
      </div>
      <div class="field mt-3 mx-2">
        <span
          class="p-float-label"
          v-tooltip.bottom="{
            value: $t('reviewGraduationData.requiredActualYear'),
            disabled: Boolean(
              studentUniversityEdu?.studentActualGraduationYear_id
            ),
          }"
        >
          <Dropdown
            id="studentActualGraduationMonth"
            class="w-full"
            v-model="studentUniversityEdu.studentActualGraduationMonth_id"
            :filter="true"
            :filterFields="['translatedName', 'name']"
            :options="translatedFormFilters.months"
            :disabled="!studentUniversityEdu.studentActualGraduationYear_id"
            optionLabel="translatedName"
            optionValue="id"
          />
          <label for="studentActualGraduationMonth"
            >{{ $t("actualMonthGraduation") }}
          </label>
        </span>
        <small
          v-for="error of v$.studentUniversityEdu
            .studentActualGraduationMonth_id.$errors"
          :key="error.$uid"
          class="p-error"
        >
          {{ error.$message }} <br />
        </small>
      </div>
    </div>
  </template>
</template>

<script setup lang="ts">
import InputText from "primevue/inputtext";
import InputNumber from "primevue/inputnumber";
import Dropdown from "primevue/dropdown";
import PageLoader from "../../shared/basic/PageLoader.vue";
import { computed, onMounted, ref, type PropType, type Ref } from "vue";
import {
  createI18nMessage,
  maxLength,
  required,
  minValue,
  maxValue,
  type MessageProps,
} from "@vuelidate/validators";
import useVuelidate from "@vuelidate/core";
import { useI18n } from "vue-i18n";
import type {
  CouncilFilters,
  StudentUniversityEdu,
  Years,
} from "@/utils/types";
import { serverTranslate } from "@/utils/filters";

// Importing Services
const { t } = useI18n();

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// Form Filters
const translatedFormFilters = computed(() => {
  return {
    grades: props.formFilters.grades?.map((grade) => ({
      ...grade,
      translatedName: grade.name ? serverTranslate(grade.name) : t("noData"),
    })),
    years: filterCurrentYears(
      props.formFilters.years?.map((year) => ({
        ...year,
        translatedName: year.name ? serverTranslate(year.name) : t("noData"),
      }))
    ),
    months: props.formFilters.months?.map((month) => ({
      ...month,
      translatedName: month.name ? serverTranslate(month.name) : t("noData"),
    })),
  };
});

// Student Data
const studentUniversityEdu = computed({
  get: () => props.studentUniversityEdu,
  set: (value) => emit("update:studentUniversityEdu", value),
});

// Computed Student Data

// Define Component Inputs (Props)
const props = defineProps({
  formFilters: {
    type: Object as PropType<CouncilFilters>,
    default: () => {
      return {};
    },
  },
  studentUniversityEdu: {
    type: Object as PropType<StudentUniversityEdu>,
    default: () => {
      return {};
    },
  },
});

// Define Component Outputs (Emits)
const emit = defineEmits(["submit", "update:studentUniversityEdu"]);

// on mount functions
onMounted(async () => {
  await v$.value.$validate();
});

// Component Functions
const filterCurrentYears = (years?: Years[]) => {
  if (years) {
    const currentCode = years.find((year) => year.current == 1)?.code;
    let filteredYears: Years[] = [];
    for (const year of years) {
      if (Number(year.code) < Number(currentCode)) {
        filteredYears.push(year);
      }
    }
    return filteredYears;
  }
  return [];
};

const clearMonthId = () => {
  if (studentUniversityEdu.value) {
    studentUniversityEdu.value.studentActualGraduationMonth_id = undefined;
  }
};

// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `reviewGraduationData.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

// Validation Rules
const rules = {
  studentUniversityEdu: {
    studentGraduationGPA: {
      requiredGba: withI18nMessage(required),
      invalidMinGba: withI18nMessage(minValue(0)),
      invalidMaxGba: withI18nMessage(maxLength(4)),
    },
    studentGraduationPercentage: {
      requiredPercentage: withI18nMessage(required),
      invalidMinPercentage: withI18nMessage(minValue(50)),
      invalidMaxPercentage: withI18nMessage(maxValue(100)),
    },
    studentGraduationEquivalentHours: {
      invalidMinEquivHours: withI18nMessage(minValue(0)),
    },
    studentSpecialization: {
      textFieldMaxLength: withI18nMessage(maxLength(100)),
    },
    studentDivision: {
      textFieldMaxLength: withI18nMessage(maxLength(100)),
    },
    studentActualGraduationYear_id: {
      requiredActualYear: withI18nMessage(required),
    },
    studentActualGraduationMonth_id: {
      requiredActualMonth: withI18nMessage(required),
    },
  },
};

// Set up component Validation
const v$ = useVuelidate(rules, { studentUniversityEdu });
</script>

<style scoped lang="scss"></style>
