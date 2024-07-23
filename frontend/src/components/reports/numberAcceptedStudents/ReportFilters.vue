<template>
  <SearchFilters
    :errorMsg="errorMsg"
    :initQuery="initQuery"
    :filters="translatedFilters"
    :rules="rules"
    @queryMounted="onQueryMount"
  >
    <template #simplefields="slotProps">
      <div class="grid-container columns-2">
        <div class="field px-2 m-0 mt-4">
          <span class="p-float-label">
            <Dropdown
              id="year"
              class="w-full"
              v-model="slotProps.query.year"
              :options="slotProps.filters.years"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              :resetFilterOnHide="true"
              optionLabel="translatedName"
              optionValue="selectedValue"
            />
            <label for="year">{{ $t("enrollmentYear") }} </label>
          </span>
          <small
            v-for="error of slotProps.v$.year.$errors"
            :key="error.$uid"
            class="p-error"
          >
            {{ error.$message }} <br />
          </small>
        </div>
        <div class="field px-2 m-0 mt-4">
          <span class="p-float-label">
            <MultiSelect
              id="registrationTypes"
              class="w-full"
              v-model="slotProps.query.registrationTypes"
              :options="slotProps.filters.registrationTypes"
              :showClear="true"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              optionLabel="translatedName"
              optionValue="selectedValue"
            />
            <label for="registrationTypes">{{ $t("registrationType") }} </label>
          </span>
        </div>
      </div>
    </template>
  </SearchFilters>
</template>

<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import Dropdown from "primevue/dropdown";
import MultiSelect from "primevue/multiselect";
import SearchFilters from "../../shared/filters/SearchFilters.vue";
import { type Ref, ref, computed } from "vue";
import type { CouncilFilters, Years } from "@/utils/types";
import { useI18n } from "vue-i18n";
import { serverTranslate } from "@/utils/filters";
import { NumberAcceptedStudentsProvider } from "@/providers/reports/numberAcceptedStudents";
import {
  type MessageProps,
  createI18nMessage,
  required,
} from "@vuelidate/validators";

// Importing Services
const { t } = useI18n();

// Static Values
const initQuery = {};

// Dynamic Values
const responseFilters: Ref<CouncilFilters> = ref({});
const translatedFilters = computed(() => {
  return {
    years: filterCurrentYears(
      responseFilters.value.years?.map((year) => ({
        ...year,
        selectedValue: year.id.toString(),
        translatedName: year.name ? serverTranslate(year.name) : t("noData"),
      })),
      true
    ),
    registrationTypes: responseFilters.value.registrationTypes?.map(
      (registrationType) => ({
        ...registrationType,
        selectedValue: registrationType.id?.toString(),
        translatedName: registrationType.name
          ? serverTranslate(registrationType.name)
          : t("noData"),
      })
    ),
  };
});
const errorMsg: Ref<string> = ref("");

// Define Component Outputs (Emits)
const emit = defineEmits(["filters"]);

// On Mount Functions
const onQueryMount = async () => {
  await getReportsFilters();
};

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

// Provider Functions
const getReportsFilters = async () => {
  const filterResponse = await NumberAcceptedStudentsProvider.filters();
  responseFilters.value = filterResponse.payload;
  emit("filters", filterResponse.payload);
};

// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `reportsFiltersValidations.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

// Validation Rules
const rules = {
  year: {
    requiredYear: withI18nMessage(required),
  },
};
</script>

<style lang="scss" scoped>
.grid-container {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
}
@media screen and (min-width: 768px) {
  .grid-container {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media screen and (min-width: 992px) {
  .grid-container {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    &.columns-3 {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
    &.columns-4 {
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }
  }
}
</style>
