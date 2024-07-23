<template>
  <PageLoader
    v-if="isLoading || errorMessage"
    :loading="isLoading"
    :error="errorMessage"
  />
  <template v-else>
    <form @submit.prevent="submitStudentForm" form="AddEditCDStudentForm">
      <div
        class="header grid justify-content-between pt-2 px-2 md:flex-row flex-column"
      >
        <div class="form-container flex-grow-1">
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="year"
                class="w-full"
                v-model="studentMilitaryEdu.militaryEduYear_id"
                :options="translatedFormFilters.years"
                optionLabel="translatedName"
                optionValue="id"
              />
              <label for="year">{{ $t("militaryEduYear") }} </label>
            </span>
            <small
              v-for="error of v$.studentMilitaryEdu.militaryEduYear_id.$errors"
              :key="error.$uid"
              class="p-error md:absolute"
            >
              {{ error.$message }} <br />
            </small>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="year"
                class="w-full"
                v-model="studentMilitaryEdu.militaryEduMonth_id"
                :options="translatedFormFilters.months"
                optionLabel="translatedName"
                optionValue="id"
              />
              <label for="year">{{ $t("militaryEduMonth") }} </label>
            </span>
            <small
              v-for="error of v$.studentMilitaryEdu.militaryEduMonth_id.$errors"
              :key="error.$uid"
              class="p-error md:absolute"
            >
              {{ error.$message }} <br />
            </small>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="grade"
                class="w-full"
                v-model="studentMilitaryEdu.militaryEduGrade_id"
                :options="translatedFormFilters.acedemicGrades"
                optionLabel="translatedName"
                optionValue="id"
              />
              <label for="grade">{{ $t("militaryEduGrade") }} </label>
            </span>
            <small
              v-for="error of v$.studentMilitaryEdu.militaryEduGrade_id.$errors"
              :key="error.$uid"
              class="p-error md:absolute"
            >
              {{ error.$message }} <br />
            </small>
          </div>
        </div>
        <div class="flex align-items-center btn-wrapper md:w-auto w-full">
          <Button
            :label="$t('save')"
            type="submit"
            class="save-button p-button p-button-primary p-button-sm flex-grow-1 mx-2 my-auto"
          />
          <Button
            v-if="props.isEdit"
            :label="$t('cancel')"
            type="button"
            class="p-button p-button-secondary p-button-sm flex-grow-1 mx-2 my-auto"
            @click="cancel()"
          />
        </div>
      </div>
    </form>
  </template>
</template>

<script setup lang="ts">
import Button from "primevue/button";
import Dropdown from "primevue/dropdown";
import PageLoader from "../shared/basic/PageLoader.vue";
import { computed, onMounted, ref, type Ref } from "vue";
import {
  createI18nMessage,
  required,
  type MessageProps,
} from "@vuelidate/validators";
import useVuelidate from "@vuelidate/core";
import { useI18n } from "vue-i18n";
import type { CouncilFilters, StudentMilitaryEdu, Years } from "@/utils/types";
import { showErrorToastMessage, showToastMessage } from "@/utils/globals";
import { serverTranslate } from "@/utils/filters";
import { MilitaryEducationProvider } from "@/providers/militaryEducation";

// Importing Services
const { t } = useI18n();

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// Form Filters
const formFilters: Ref<CouncilFilters> = ref({});
const translatedFormFilters = computed(() => {
  return {
    years: filterCurrentYears(
      formFilters.value.years?.map((year) => ({
        ...year,
        translatedName: year.name ? serverTranslate(year.name) : t("noData"),
      }))
    ),
    months: formFilters.value.months?.map((month) => ({
      ...month,
      translatedName: month.name ? serverTranslate(month.name) : t("noData"),
    })),
    acedemicGrades: formFilters.value.acedemicGrades?.map((acedemicGrade) => ({
      ...acedemicGrade,
      translatedName: acedemicGrade.name
        ? serverTranslate(acedemicGrade.name)
        : t("noData"),
    })),
  };
});

// Student Data
const studentMilitaryEdu: Ref<StudentMilitaryEdu> = ref({});

// Define Component Inputs (Props)
const props = defineProps({
  isEdit: { type: Boolean, default: true },
  studentId: { type: Number, default: 13 },
});

// Define Component Outputs (Emits)
const emit = defineEmits(["cancel", "submit"]);

// on mount functions
onMounted(async () => {
  if (props.isEdit && props.studentId) {
    await getStudentData(props.studentId);
    await v$.value.$validate();
  } else {
    await getDefaults(props.studentId);
  }
});

// Component Functions
const filterCurrentYears = (years?: Years[]) => {
  if (years) {
    const currentCode = years.find((year) => year.current == 1)?.code;
    let filteredYears: Years[] = [];
    for (const year of years) {
      if (Number(year.code) <= Number(currentCode)) {
        filteredYears.push(year);
      }
    }
    return filteredYears;
  }
  return [];
};

// Component Functions
const cancel = () => {
  emit("cancel");
};

// Provider related Functions
const getDefaults = async (Id: number) => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    // Gets GS Defaults
    const result = await MilitaryEducationProvider.formFilters(Id);
    formFilters.value = result.payload;
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const getStudentData = async (Id: number) => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const result = await MilitaryEducationProvider.getStudentData(Id);
    studentMilitaryEdu.value = result.payload.studentMilitaryEdu;
    await getDefaults(Id);
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const submitStudentForm = async () => {
  const isValid = await v$.value.$validate();
  isLoading.value = true;
  if (isValid) {
    try {
      if (props.isEdit) {
        const result = await MilitaryEducationProvider.editStudentData(
          props.studentId,
          studentMilitaryEdu.value
        );
        showToastMessage(result.detail);
      } else {
        const result = await MilitaryEducationProvider.addStudentData(
          props.studentId,
          studentMilitaryEdu.value
        );
        showToastMessage(result.detail);
      }
      emit("submit", studentMilitaryEdu.value);
    } catch (error) {
      showErrorToastMessage(error);
    }
  }
  isLoading.value = false;
};

// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `militaryEduValidations.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

// Validation Rules
const rules = {
  studentMilitaryEdu: {
    militaryEduYear_id: {
      requiredYear: withI18nMessage(required),
    },
    militaryEduMonth_id: {
      requiredMonth: withI18nMessage(required),
    },
    militaryEduGrade_id: {
      requiredGrade: withI18nMessage(required),
    },
  },
};

// Set up component Validation
const v$ = useVuelidate(rules, {
  studentMilitaryEdu,
});
</script>

<style scoped lang="scss">
.btn-wrapper {
  margin-inline-start: auto;
}
.save-button {
  min-width: 6rem;
}
</style>
