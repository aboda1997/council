<template>
  <Dialog
    :header="$t('addNewStudent')"
    v-model:visible="showAddPopup"
    :dismissableMask="true"
    class="add-student-popup"
    :breakpoints="{ '960px': '75vw', '640px': '90vw' }"
    :style="{ width: '50vw' }"
    :modal="true"
  >
    <PageLoader
      v-if="isLoading || errorMessage"
      :loading="isLoading"
      :error="errorMessage"
    />
    <template v-else>
      <div :class="['form-container', singleColumnCass]">
        <div class="field mt-3 mx-2">
          <span class="p-float-label">
            <Dropdown
              id="certificate"
              class="w-full"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              v-model="studentSecondaryEdu.studentSecondaryCert_id"
              :options="translatedFilters.certificates"
              optionLabel="translatedName"
              optionValue="id"
            />
            <label for="certificate">{{ $t("certificate") }} </label>
          </span>
          <small
            v-for="error of v$.studentSecondaryEdu.studentSecondaryCert_id
              .$errors"
            :key="error.$uid"
            class="p-error"
          >
            {{ error.$message }} <br />
          </small>
        </div>
        <div class="field mt-3 mx-2" v-if="isGSCertificate">
          <span class="p-float-label">
            <Dropdown
              id="certYear"
              class="w-full"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              v-model="studentSecondaryEdu.studentCertificateYear_id"
              :options="translatedFilters.years"
              optionLabel="translatedName"
              optionValue="id"
            />
            <label for="certYear">{{ $t("certYear") }} </label>
          </span>
          <small
            v-for="error of v$.studentSecondaryEdu.studentCertificateYear_id
              .$errors"
            :key="error.$uid"
            class="p-error"
          >
            {{ error.$message }} <br />
          </small>
        </div>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-content-end">
        <template v-if="errorMessage">
          <Button
            :label="$t('no')"
            @click="cancelPopup"
            class="p-button-text"
          />
        </template>
        <template v-else-if="!isLoading && !errorMessage">
          <Button
            :label="$t('yes')"
            @click="acceptPopup"
            class="p-button-primary"
            autofocus
          />
          <Button
            :label="$t('no')"
            @click="cancelPopup"
            class="p-button-text"
          />
        </template>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import Dropdown from "primevue/dropdown";
import PageLoader from "../shared/basic/PageLoader.vue";
import { useI18n } from "vue-i18n";
import { computed, onMounted, ref, type PropType, type Ref } from "vue";
import type {
  CouncilFilters,
  InquireStudentQuery,
  SecondaryGSInfo,
  StudentSecondaryEdu,
  Years,
} from "@/utils/types";
import useVuelidate from "@vuelidate/core";
import {
  createI18nMessage,
  required,
  type MessageProps,
} from "@vuelidate/validators";
import { InquireStudentInfoProvider } from "@/providers/inquireStudentInfo";
import { CertificateEnum, ToastTypes } from "@/utils/enums";
import { serverTranslate } from "@/utils/filters";
import { showErrorToastMessage } from "@/utils/globals";

// Import Services
const { t } = useI18n();

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// Component Data
const filters: Ref<CouncilFilters> = ref({});
const translatedFilters: Ref<CouncilFilters> = computed(() => {
  return {
    ...filters.value,
    certificates: filters.value.certificates?.map((certificate) => ({
      ...certificate,
      selectedValue: certificate.id.toString(),
      translatedName: certificate.name
        ? serverTranslate(certificate.name)
        : t("noData"),
    })),
    years: filterCurrentYears(
      filters.value.years?.map((year) => ({
        ...year,
        selectedValue: year.id.toString(),
        translatedName: year.name ? serverTranslate(year.name) : t("noData"),
      })),
      false
    ),
  };
});
const showAddPopup = computed({
  get: () => props.showAddPopup,
  set: (value) => emit("update:showAddPopup", value),
});
const studentSecondaryEdu = computed({
  get: () => props.studentSecondaryEdu,
  set: (value) => emit("update:studentSecondaryEdu", value),
});
const isGSCertificate = computed(() => {
  return (
    studentSecondaryEdu.value.studentSecondaryCert_id ===
    CertificateEnum.EGYPTIAN_GENERAL_SECONADARY
  );
});
const singleColumnCass = computed(() => {
  return !isGSCertificate.value ? "single-column" : "";
});

// Define Component Inputs (Props)
const props = defineProps({
  searchQuery: {
    type: Object as PropType<InquireStudentQuery>,
    default: null,
  },
  showAddPopup: {
    type: Boolean,
    default: false,
  },
  studentSecondaryEdu: {
    type: Object as PropType<StudentSecondaryEdu>,
    default: null,
  },
});

// Define Component Outputs (Emits)
const emit = defineEmits([
  "update:showAddPopup",
  "update:studentSecondaryEdu",
  "add",
]);

// Component Functions
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

const cancelPopup = () => {
  showAddPopup.value = false;
};

const acceptPopup = async () => {
  const isFormValid = await v$.value.$validate();
  if (isFormValid) {
    let result: SecondaryGSInfo = {
      studentSecondaryEdu: {
        studentSecondaryCert_id:
          studentSecondaryEdu.value.studentSecondaryCert_id,
      },
    };
    if (isGSCertificate.value) {
      result.studentSecondaryEdu = { ...studentSecondaryEdu.value };
      const info = await getSecondaryGSInfo();
      if (info) {
        result = info;
      }
    }
    emit("add", result);
    showAddPopup.value = false;
  }
};

// On Mount Action
onMounted(async () => {
  await getPopupForm();
  await v$.value.$validate();
});

// Provider functions
const getPopupForm = async () => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const result = await InquireStudentInfoProvider.popupfilters();
    filters.value = result.payload;
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const getSecondaryGSInfo = async () => {
  isLoading.value = true;
  let result: SecondaryGSInfo | undefined = undefined;
  try {
    const response = await InquireStudentInfoProvider.getSecondaryGSInfo(
      props.searchQuery.nationalID || "",
      studentSecondaryEdu.value.studentSecondaryCert_id || 0,
      studentSecondaryEdu.value.studentCertificateYear_id || 0
    );
    result = response.payload;
  } catch (error) {
    const payload = error as string;
    let toastType = ToastTypes.ERROR;
    if (payload.includes("does not exist")) {
      toastType = ToastTypes.WARN;
    }
    showErrorToastMessage(error, toastType);
  }
  isLoading.value = false;
  return result;
};

// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `addEditStudentValidations.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

// Custom Validation Rules
const checkRequiredIfGS = (value: TemplateStringsArray) => {
  if (isGSCertificate.value) {
    return Boolean(value);
  }
  return true;
};

const rules = {
  studentSecondaryEdu: {
    studentSecondaryCert_id: {
      checkCertificate: withI18nMessage(required),
    },
    studentCertificateYear_id: {
      checkCertificateYear: withI18nMessage(checkRequiredIfGS),
    },
  },
};
const v$ = useVuelidate(rules, { studentSecondaryEdu });
</script>

<style scoped lang="scss">
.add-student-popup {
  padding: 0 1rem !important;
}
.form-container {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
}
@media screen and (min-width: 768px) {
  .form-container {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
.single-column {
  grid-template-columns: minmax(0, 1fr) !important;
}
</style>
