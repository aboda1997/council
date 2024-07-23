<template>
  <div v-if="studentUniversityEdu" class="form-container">
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="studentPrevUniveristy"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentUniversityEdu.studentPrevUniveristy_id"
          :options="translatedFormFilters.universities"
          :disabled="true"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="studentPrevUniveristy"
          >{{ $t("prevEnrollmentUniveristy") }}
        </label>
      </span>
    </div>
    <div class="field mt-3 mx-2" v-if="!isExternalUni">
      <span class="p-float-label">
        <Dropdown
          id="studentPrevFaculty"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentUniversityEdu.studentPrevFaculty_id"
          :options="translatedFormFilters.faculties"
          :disabled="true"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="studentPrevFaculty"
          >{{ $t("prevEnrollmentFaculty") }}
        </label>
      </span>
    </div>
    <div class="field mt-3 mx-2" v-if="isExternalUni">
      <span class="p-float-label">
        <InputText
          id="prevEnrollmentCustomExternal"
          class="w-full"
          type="text"
          :disabled="true"
          v-model="studentUniversityEdu.studentPrevCustomUniversityFaculty"
        />

        <label for="prevEnrollmentCustomExternal"
          >{{ $t("prevEnrollmentCustomExternal") }}
        </label>
      </span>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="studentPrevEnrollYear_id"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentUniversityEdu.studentPrevEnrollYear_id"
          :options="translatedFormFilters.years"
          :disabled="true"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="studentPrevEnrollYear_id"
          >{{ $t("prevEnrollmentYear") }}
        </label>
      </span>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="studentPrevEnrollSemester"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentUniversityEdu.studentPrevEnrollSemester_id"
          :options="translatedFormFilters.semesters"
          :disabled="true"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="studentPrevEnrollSemester"
          >{{ $t("prevEnrollmentSemester") }}
        </label>
      </span>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="studentPrevEnrollStage"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentUniversityEdu.studentPrevEnrollStage_id"
          :options="translatedFormFilters.stages"
          :disabled="true"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="studentPrevEnrollStage">
          {{ $t("prevEnrollmentStage") }}
        </label>
      </span>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <InputText
          id="transferDate"
          class="w-full"
          type="text"
          :disabled="true"
          v-model="studentUniversityEdu.transferDate"
        />

        <label for="transferDate">{{ $t("transferDate") }} </label>
      </span>
    </div>
  </div>
  <div class="form-container">
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="studentLevel"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentUniversityEdu.studentLevel_id"
          :options="translatedFormFilters.levels"
          :disabled="disableStatus"
          :showClear="true"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="studentLevel">{{ $t("transferLevel") }} </label>
      </span>
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
          :disabled="disableStatus"
          v-model="studentUniversityEdu.totalEquivalentHours"
        />
        <label for="totalEquivHours">{{ $t("totalEquivHours") }} </label>
      </span>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="fulFillmentReasons"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentUniversityEdu.transferFulfillment_id"
          :options="translatedFormFilters.fulfillments"
          :disabled="disableStatus"
          :showClear="true"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="fulFillmentReasons">{{ $t("fulFillmentReasons") }} </label>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import Dropdown from "primevue/dropdown";
import InputNumber from "primevue/inputnumber";
import InputText from "primevue/inputtext";
import { computed, onMounted, type PropType } from "vue";
import useVuelidate from "@vuelidate/core";
import { useI18n } from "vue-i18n";
import type { CouncilFilters, StudentUniversityEdu } from "@/utils/types";
import { serverTranslate } from "@/utils/filters";
import {
  FulfillmentTypeEnum,
  StudentStatus,
  UniversityIdEnum,
} from "@/utils/enums";

// Importing Services
const { t } = useI18n();

// Form Filters
const translatedFormFilters = computed(() => {
  return {
    years: props.formFilters.years?.map((year) => ({
      ...year,
      translatedName: year.name ? serverTranslate(year.name) : t("noData"),
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
    universities: props.formFilters.universities?.map((university) => ({
      ...university,
      translatedName: university.name
        ? serverTranslate(university.name)
        : t("noData"),
    })),
    faculties: props.formFilters.faculties?.map((faculty) => ({
      ...faculty,
      translatedName: faculty.name
        ? serverTranslate(faculty.name)
        : t("noData"),
    })),
    levels: props.formFilters.levels?.map((level) => ({
      ...level,
      translatedName: level.name ? serverTranslate(level.name) : t("noData"),
    })),
    fulfillments: props.formFilters.fulfillments
      ?.filter(
        (fulfillment) =>
          fulfillment.typeid ==
          FulfillmentTypeEnum.TRANSFER_FULFILLMENT.toString()
      )
      .map((fulfillment) => ({
        ...fulfillment,
        translatedName: fulfillment.name
          ? serverTranslate(fulfillment.name)
          : t("noData"),
      })),
  };
});

// Computed Student Data
const disableStatus = computed(() => {
  return props.studentStatusId == StudentStatus.INITIALLY_ACCEPTED;
});
const isExternalUni = computed(() => {
  if (studentUniversityEdu.value) {
    return (
      studentUniversityEdu.value.studentPrevUniveristy_id ==
      UniversityIdEnum.EXTERNAL
    );
  }
  return false;
});
const studentUniversityEdu = computed({
  get: () => props.studentUniversityEdu,
  set: (value) => emit("update:studentUniversityEdu", value),
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

// Validation Rules
const rules = {};

// Set up component Validation
const v$ = useVuelidate(rules, {});
</script>

<style scoped lang="scss"></style>
