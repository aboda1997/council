<template>
  <SearchFilters :rules="rules" :filters="translatedFilters">
    <template #simplefields="slotProps">
      <div class="field mt-3 lg:col-3 md:col-6 col-12 m-0">
        <span class="p-float-label">
          <Dropdown
            class="w-full"
            v-model="slotProps.query.selectedYear"
            :options="slotProps.filters.years"
            optionLabel="translatedName"
            optionValue="code"
          />
          <label for="selectedYear">{{ $t("academicYear") }} </label>
        </span>
        <small
          v-for="error of slotProps.v$.selectedYear.$errors"
          :key="error.$uid"
          class="p-error"
        >
          {{ error.$message }} <br />
        </small>
      </div>
      <div class="field mt-3 lg:col-3 md:col-6 col-12 m-0">
        <span class="p-float-label">
          <Dropdown
            class="w-full"
            v-model="slotProps.query.searchType"
            :options="slotProps.filters.searchTypes"
            optionLabel="translatedName"
            optionValue="name"
            @change="slotProps.clearField('search')"
          />
          <label for="searchType">{{ $t("searchType") }}</label>
        </span>
        <small
          v-for="error of slotProps.v$.searchType.$errors"
          :key="error.$uid"
          class="p-error"
        >
          {{ error.$message }} <br />
        </small>
      </div>
      <div class="field mt-3 lg:col-6 md:col-12 col-12 m-0">
        <span
          class="p-float-label"
          v-tooltip.bottom="{
            value: $t('inqueryCDFiltersValidations.requiredSearchType'),
            disabled: slotProps.query.searchType,
          }"
        >
          <InputText
            class="w-full"
            type="text"
            v-model="slotProps.query.search"
            @input="
              checkStudentNameInput(slotProps.query.search, slotProps.query)
            "
            :disabled="!slotProps.query.searchType"
          />
          <label for="search">{{ $t("searchKeyword") }}</label>
        </span>
        <small
          v-for="error of slotProps.v$.search.$errors"
          :key="error.$uid"
          class="p-error"
        >
          {{ error.$message }} <br />
        </small>
      </div>
    </template>
  </SearchFilters>
</template>

<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import InputText from "primevue/inputtext";
import Dropdown from "primevue/dropdown";
import SearchFilters from "../shared/filters/SearchFilters.vue";
import { type Ref, ref, computed, onMounted } from "vue";
import { InquireCDStudentProvider } from "@/providers/inquireCDStudent";
import type {
  BasicAttribute,
  CouncilFilters,
  InquireCDStudentQuery,
  Years,
} from "@/utils/types";
import {
  createI18nMessage,
  required,
  type MessageProps,
} from "@vuelidate/validators";
import { useI18n } from "vue-i18n";
import {
  IntegerPattern,
  NIDPattern,
  NoSymbolsPattern,
  FiltersSearchType,
  SymbolsPattern,
  NonDigitsPattern,
} from "@/utils/enums";
import { serverTranslate } from "@/utils/filters";

// Importing Services
const { t } = useI18n();

// Dynamic Values
const responseFilters: Ref<CouncilFilters> = ref({});
const translatedFilters: Ref<CouncilFilters> = computed(() => {
  return {
    years: filterCurrentYears(
      responseFilters.value.years?.map((year) => ({
        ...year,
        translatedName: year.name ? serverTranslate(year.name) : t("noData"),
      }))
    ),
    searchTypes: searchTypes.map((type) => ({
      ...type,
      translatedName: type.name ? t(type.name) : t("noData"),
    })),
  };
});

// Static Values
const searchTypes: BasicAttribute[] = [
  { name: FiltersSearchType.NATIONAL_ID },
  { name: FiltersSearchType.SEAT_NUMBER },
  { name: FiltersSearchType.STUDENT_NAME },
];

// On Mount Functions
onMounted(async () => {
  await getCouncilFilters();
});

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

const getCouncilFilters = async () => {
  const filterResponse = await InquireCDStudentProvider.filters();
  responseFilters.value = filterResponse.payload;
};

// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `inqueryCDFiltersValidations.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

// Form Validation Rules
const checkEachNameLength = (
  value: string,
  siblings: InquireCDStudentQuery
): boolean => {
  if (value && siblings.searchType === "studentName") {
    const nameLengthsArray = value.split(" ").map((w: string) => w.length);
    const filteredLengths = nameLengthsArray.filter(
      (value: number) => value > 0
    );
    for (const length of filteredLengths) {
      if (length < 2) {
        return false;
      }
    }
  }
  return true;
};

const checkStudentNameInput = (
  search: string,
  query: { search: string; searchType: string }
) => {
  switch (query.searchType) {
    case FiltersSearchType.NATIONAL_ID:
      query.search = search.replace(NonDigitsPattern, "");
      break;
    case FiltersSearchType.SEAT_NUMBER:
      query.search = search.replace(NonDigitsPattern, "");
      break;
    case FiltersSearchType.STUDENT_NAME:
      query.search = search.replace(SymbolsPattern, "");
      break;
  }
};

const checkNameLength = (
  value: string,
  siblings: InquireCDStudentQuery
): boolean => {
  if (value && siblings.searchType === "studentName") {
    const nameLengthsArray = value.split(" ").map((w: string) => w.length);
    const filteredLengths = nameLengthsArray.filter(
      (value: number) => value > 0
    );
    return filteredLengths.length > 1;
  }
  return true;
};

const checkTotalNameLength = (
  value: string,
  siblings: InquireCDStudentQuery
): boolean => {
  if (value && siblings.searchType === "studentName") {
    return value.length < 100;
  }
  return true;
};

const checkStudentNameText = (
  value: string,
  siblings: InquireCDStudentQuery
): boolean => {
  if (value && siblings.searchType === "studentName") {
    return NoSymbolsPattern.test(value);
  }
  return true;
};

const checkInteger = (
  value: string,
  siblings: InquireCDStudentQuery
): boolean => {
  if (
    value &&
    siblings.searchType &&
    [FiltersSearchType.SEAT_NUMBER, FiltersSearchType.NATIONAL_ID].includes(
      siblings.searchType
    )
  ) {
    return IntegerPattern.test(value);
  }
  return true;
};
const checkSeatNumberLength = (
  value: string,
  siblings: InquireCDStudentQuery
): boolean => {
  if (value && siblings.searchType === FiltersSearchType.SEAT_NUMBER) {
    return value.length <= 9;
  }
  return true;
};

const checkNIDNumberLength = (
  value: string,
  siblings: InquireCDStudentQuery
): boolean => {
  if (value && siblings.searchType === FiltersSearchType.NATIONAL_ID) {
    return value.length == 14;
  }
  return true;
};

const checkNIDNumber = (
  value: string,
  siblings: InquireCDStudentQuery
): boolean => {
  if (value && siblings.searchType === FiltersSearchType.NATIONAL_ID) {
    return NIDPattern.test(value);
  }
  return true;
};

// Validation Rules
const rules = {
  selectedYear: {
    requiredYear: withI18nMessage(required),
  },
  searchType: {
    requiredSearchType: withI18nMessage(required),
  },
  search: {
    requiredSearchData: withI18nMessage(required),
    requiredStudentNameLength: withI18nMessage(checkNameLength),
    requiredStudentEachNameLength: withI18nMessage(checkEachNameLength),
    requiredStudentNameFullLength: withI18nMessage(checkTotalNameLength),
    checkStudentNameText: withI18nMessage(checkStudentNameText),
    checkInteger: withI18nMessage(checkInteger),
    checkSeatNumberLength: withI18nMessage(checkSeatNumberLength),
    checkNIDNumberLength: withI18nMessage(checkNIDNumberLength),
    checkNIDNumber: withI18nMessage(checkNIDNumber),
  },
};
</script>

<style scoped></style>
