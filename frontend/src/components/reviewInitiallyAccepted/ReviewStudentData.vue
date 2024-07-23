<template>
  <PageLoader
    v-if="isLoading || errorMessage"
    :loading="isLoading"
    :error="errorMessage"
  />
  <template v-else>
    <form @submit.prevent="submit" form="AddEditCDStudentForm">
      <div
        v-if="props.selectedStudents && props.selectedStudents.length"
        class="flex flex-row align-items-center mb-1"
      >
        <span>{{ $t("numberOf") }}</span>
        <span class="mx-1 text-primary font-bold mb-1">
          {{ props.selectedStudents ? props.selectedStudents.length : 0 }}
        </span>
        <span>{{ $t("selectedStudentChange") }}</span>
      </div>
      <div v-else class="flex flex-row align-items-center">
        <span class="p-error">{{ $t("mustSelectStudents") }}</span>
      </div>
      <div
        class="header grid justify-content-between p-2 md:flex-row flex-column md:relative"
      >
        <div
          class="form-container flex-grow-1"
          :class="hasFulfillmentStatus ? 'two-item' : ''"
        >
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="year"
                class="w-full"
                v-model="studentStatusId"
                :options="translatedFormFilters.status"
                :disabled="
                  !props.selectedStudents || !props.selectedStudents.length
                "
                optionLabel="translatedName"
                optionValue="id"
              />
              <label for="year">{{ $t("studentStatus") }} </label>
            </span>
            <small
              v-for="error of v$.studentStatusId.$errors"
              :key="error.$uid"
              class="p-error md:absolute"
            >
              {{ error.$message }} <br />
            </small>
          </div>
          <div class="field mt-3 mx-2" v-if="hasFulfillmentStatus">
            <span class="p-float-label">
              <Dropdown
                id="grade"
                class="w-full"
                v-model="studentFulfillment"
                :options="translatedFormFilters.fulfillments"
                :disabled="
                  !props.selectedStudents || !props.selectedStudents.length
                "
                optionLabel="translatedName"
                optionValue="id"
              />
              <label for="grade">{{ $t("fulFillment") }} </label>
            </span>
            <small
              v-for="error of v$.studentFulfillment.$errors"
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
            :disabled="
              !props.selectedStudents || !props.selectedStudents.length
            "
            type="submit"
            class="save-button p-button p-button-primary p-button-sm flex-grow-1 mx-2 my-auto"
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
import { computed, onMounted, ref, type Ref, type PropType } from "vue";
import {
  createI18nMessage,
  required,
  type MessageProps,
} from "@vuelidate/validators";
import useVuelidate from "@vuelidate/core";
import { useI18n } from "vue-i18n";
import type { CouncilFilters, StudentListing } from "@/utils/types";
import {
  showConfirmDialog,
  showErrorToastMessage,
  showToastMessage,
} from "@/utils/globals";
import { serverTranslate } from "@/utils/filters";
import { ReviewInitiallyAcceptedProvider } from "@/providers/reviewInitiallyAccepted";
import { StudentStatus } from "@/utils/enums";

// Importing Services
const { t } = useI18n();

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// Form Filters
const formFilters: Ref<CouncilFilters> = ref({});
const translatedFormFilters = computed(() => {
  return {
    status: formFilters.value.status?.map((status) => ({
      ...status,
      translatedName: status.name ? serverTranslate(status.name) : t("noData"),
    })),
    fulfillments: formFilters.value.fulfillments?.map((fulfillment) => ({
      ...fulfillment,
      translatedName: fulfillment.name
        ? serverTranslate(fulfillment.name)
        : t("noData"),
    })),
  };
});

// Student Data
const studentStatusId: Ref<number | undefined> = ref();
const studentFulfillment: Ref<number | undefined> = ref();

// Computed Values
const hasFulfillmentStatus = computed(() => {
  return studentStatusId.value === StudentStatus.FULFILLMENT;
});

// Define Component Inputs (Props)
const props = defineProps({
  selectedStudents: {
    type: Array as PropType<StudentListing[]>,
    default: () => {
      return [];
    },
  },
});

// Define Component Outputs (Emits)
const emit = defineEmits(["cancel", "submit"]);

// on mount functions
onMounted(async () => {
  await getDefaults();
});

// Component Functions
const submit = async () => {
  const isValid = await v$.value.$validate();
  if (isValid) {
    showConfirmDialog(t("confirmSelectedChange"), (confirm: boolean) => {
      if (confirm) {
        submitStudentForm();
      }
    });
  }
};

// Provider related Functions
const getDefaults = async () => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    // Gets GS Defaults
    const result = await ReviewInitiallyAcceptedProvider.formFilters();
    formFilters.value = result.payload;
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const submitStudentForm = async () => {
  isLoading.value = true;
  try {
    const studentIds = props.selectedStudents.map((student) => student.id);
    const result = await ReviewInitiallyAcceptedProvider.editStudentData(
      studentIds,
      studentStatusId.value,
      studentFulfillment.value
    );
    showToastMessage(result.detail);
    v$.value.$reset();
    emit("submit");
  } catch (error) {
    showErrorToastMessage(error);
  }

  isLoading.value = false;
};

// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `addEditStudentValidations.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

// Custom Validators
const checkStudentFulfillment = (value: TemplateStringsArray) => {
  if (hasFulfillmentStatus.value) {
    return Boolean(value);
  }
  return true;
};

// Validation Rules
const rules = {
  studentStatusId: {
    checkStatus: withI18nMessage(required),
  },
  studentFulfillment: {
    checkStudentFulfillment: withI18nMessage(checkStudentFulfillment),
  },
};

// Set up component Validation
const v$ = useVuelidate(rules, {
  studentStatusId,
  studentFulfillment,
});
</script>

<style scoped lang="scss">
.form-container {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
}
@media screen and (min-width: 768px) {
  .form-container {
    &.two-item {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }
}
.btn-wrapper {
  margin-inline-start: auto;
}
.save-button {
  min-width: 6rem;
}
</style>
