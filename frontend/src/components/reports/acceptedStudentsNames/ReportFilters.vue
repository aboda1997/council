<template>
  <SearchFilters
    :errorMsg="errorMsg"
    :initQuery="initQuery"
    :filters="translatedFilters"
    :rules="rules"
    @queryMounted="onQueryMount"
  >
    <template #simplefields="slotProps">
      <div class="grid-container columns-3">
        <div class="field px-2 m-0 mt-4">
          <span class="p-float-label">
            <Dropdown
              id="university"
              class="w-full"
              v-model="slotProps.query.university"
              :options="slotProps.filters.universities"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              :resetFilterOnHide="true"
              optionLabel="translatedName"
              optionValue="selectedValue"
              @change="
                getFaculties(slotProps.query);
                slotProps.clearField('faculty');
              "
            />
            <label for="university">{{ $t("university") }} </label>
          </span>
          <small
            v-for="error of slotProps.v$.university.$errors"
            :key="error.$uid"
            class="p-error"
          >
            {{ error.$message }} <br />
          </small>
        </div>

        <div class="field px-2 m-0 mt-4">
          <span
            class="p-float-label"
            v-tooltip.bottom="{
              value: $t('inqueryFiltersValidations.requiredUniversity'),
              disabled: slotProps.query.university,
            }"
          >
            <Dropdown
              class="w-full"
              id="faculty"
              v-model="slotProps.query.faculty"
              :options="slotProps.filters.filterFaculties"
              :showClear="Boolean(slotProps.query.faculty)"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              optionLabel="translatedName"
              optionValue="selectedValue"
              :disabled="!slotProps.query.university"
            />
            <label for="faculty">{{ $t("faculty") }} </label>
          </span>
        </div>
        <div class="field px-2 m-0 mt-4">
          <span class="p-float-label">
            <Dropdown
              id="year"
              class="w-full"
              v-model="slotProps.query.year"
              :options="slotProps.filters.years"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              :showClear="true"
              :resetFilterOnHide="true"
              optionLabel="translatedName"
              optionValue="selectedValue"
            />
            <label for="year">{{ $t("universityEnrollmentYear") }} </label>
          </span>
          <small
            v-for="error of slotProps.v$.year.$errors"
            :key="error.$uid"
            class="p-error"
          >
            {{ error.$message }} <br />
          </small>
        </div>
      </div>
    </template>
    <template #advancedfields="slotProps">
      <div class="grid-container columns-4">
        <div class="field px-2 m-0 mt-4">
          <span class="p-float-label">
            <Dropdown
              class="w-full"
              id="semester"
              v-model="slotProps.query.semester"
              :options="slotProps.filters.semesters"
              :showClear="Boolean(slotProps.query.semester)"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              optionLabel="translatedName"
              optionValue="selectedValue"
            />
            <label for="semester"
              >{{ $t("universityEnrollmentSemester") }}
            </label>
          </span>
        </div>
        <div class="field px-2 m-0 mt-4">
          <span class="p-float-label">
            <Dropdown
              class="w-full"
              id="stage"
              v-model="slotProps.query.stage"
              :options="slotProps.filters.stages"
              :showClear="Boolean(slotProps.query.stage)"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              optionLabel="translatedName"
              optionValue="selectedValue"
            />
            <label for="stage">{{ $t("universityEnrollmentStage") }} </label>
          </span>
        </div>
        <div class="field px-2 m-0 mt-4">
          <span class="p-float-label">
            <Dropdown
              id="studentStatus"
              class="w-full"
              v-model="slotProps.query.studentStatus"
              :options="slotProps.filters.status"
              :showClear="Boolean(slotProps.query.studentStatus)"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              optionLabel="translatedName"
              optionValue="selectedValue"
            />
            <label for="studentStatus">{{ $t("studentStatus") }} </label>
          </span>
        </div>
        <div
          v-if="
            slotProps.query.studentStatus &&
            slotProps.query.studentStatus === String(StudentStatus.FULFILLMENT)
          "
          class="field px-2 m-0 mt-4"
        >
          <span class="p-float-label">
            <Dropdown
              id="fulfillment"
              class="w-full"
              v-model="slotProps.query.fulfillment"
              :options="slotProps.filters.fulfillments"
              :showClear="Boolean(slotProps.query.fulfillment)"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              optionLabel="translatedName"
              optionValue="selectedValue"
            />
            <label for="fulfillment">{{ $t("fulFillment") }} </label>
          </span>
        </div>
        <div class="field px-2 m-0 mt-4">
          <span class="p-float-label">
            <Dropdown
              id="nationality"
              class="w-full"
              v-model="slotProps.query.region"
              :options="slotProps.filters.regions"
              :showClear="Boolean(slotProps.query.region)"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              optionLabel="translatedName"
              optionValue="selectedValue"
              @change="
                !slotProps.query.region || slotProps.query.region === '1'
                  ? slotProps.clearField('passport')
                  : slotProps.clearField(['nationalID', 'passport'])
              "
            />
            <label for="nationality">{{ $t("countryOfBirth") }} </label>
          </span>
        </div>
        <div class="field px-2 m-0 mt-4">
          <span class="p-float-label">
            <Dropdown
              class="w-full"
              id="certificate"
              v-model="slotProps.query.certificate"
              :options="slotProps.filters.certificates"
              :showClear="Boolean(slotProps.query.certificate)"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              optionLabel="translatedName"
              optionValue="selectedValue"
              @change="slotProps.clearField(['seatNumber', 'gsYear'])"
            />
            <label for="certificate">{{ $t("certificate") }} </label>
          </span>
        </div>
        <div v-if="slotProps.query.certificate" class="field px-2 m-0 mt-4">
          <span class="p-float-label">
            <Dropdown
              id="gsYear"
              class="w-full"
              v-model="slotProps.query.gsYear"
              :options="slotProps.filters.gsYear"
              :showClear="Boolean(slotProps.query.gsYear)"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              optionLabel="translatedName"
              optionValue="selectedValue"
            />
            <label for="gsYear">{{ $t("gsYear") }} </label>
          </span>
        </div>
        <div class="field px-2 m-0 mt-4">
          <span class="p-float-label">
            <Dropdown
              id="registrationType"
              class="w-full"
              v-model="slotProps.query.registrationType"
              :options="slotProps.filters.registrationTypes"
              :showClear="Boolean(slotProps.query.registrationType)"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              optionLabel="translatedName"
              optionValue="selectedValue"
            />
            <label for="registrationType">{{ $t("registrationType") }} </label>
          </span>
        </div>
      </div>
    </template>
  </SearchFilters>
</template>

<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import Dropdown from "primevue/dropdown";
import SearchFilters from "../../shared/filters/SearchFilters.vue";
import { type Ref, ref, computed } from "vue";
import type { CouncilFilters, Faculty, Years } from "@/utils/types";
import { useI18n } from "vue-i18n";
import { serverTranslate } from "@/utils/filters";
import { AcceptedStudentsNamesProvider } from "@/providers/reports/acceptedStudentsNames";
import {
  type MessageProps,
  createI18nMessage,
  required,
} from "@vuelidate/validators";
import { FulfillmentTypeEnum, StudentStatus } from "@/utils/enums";

// Importing Services
const { t } = useI18n();

// Static Values
const initQuery = {};

// Dynamic Values
const responseFilters: Ref<CouncilFilters> = ref({});
const filterFaculties: Ref<Faculty[]> = ref([]);
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
    universities: responseFilters.value.universities
      ?.map((university) => ({
        ...university,
        selectedValue: university.id.toString(),
        translatedName: university.name
          ? serverTranslate(university.name)
          : t("noData"),
      }))
      .sort((a, b) => a.translatedName.localeCompare(b.translatedName)),
    gsYear: filterCurrentYears(
      responseFilters.value.years?.map((year) => ({
        ...year,
        selectedValue: year.id.toString(),
        translatedName: year.name ? serverTranslate(year.name) : t("noData"),
      })),
      false
    ),
    registrationTypes: responseFilters.value.registrationTypes?.map(
      (registrationType) => ({
        ...registrationType,
        selectedValue: registrationType.id.toString(),
        translatedName: registrationType.name
          ? serverTranslate(registrationType.name)
          : t("noData"),
      })
    ),
    status: responseFilters.value.status?.map((status) => ({
      ...status,
      selectedValue: status.id.toString(),
      translatedName: status.name ? serverTranslate(status.name) : t("noData"),
    })),
    regions: responseFilters.value.countries
      ?.map((region) => ({
        ...region,
        selectedValue: region.id.toString(),
        translatedName: region.name
          ? serverTranslate(region.name)
          : t("noData"),
      }))
      .sort((a, b) => a.translatedName.localeCompare(b.translatedName)),
    semesters: responseFilters.value.semesters?.map((semester) => ({
      ...semester,
      selectedValue: semester.id.toString(),
      translatedName: semester.name
        ? serverTranslate(semester.name)
        : t("noData"),
    })),
    stages: responseFilters.value.stages?.map((stage) => ({
      ...stage,
      selectedValue: stage.id.toString(),
      translatedName: stage.name ? serverTranslate(stage.name) : t("noData"),
    })),
    fulfillments: responseFilters.value.fulfillments
      ?.filter(
        (fulfillment) =>
          fulfillment.typeid ==
          FulfillmentTypeEnum.SECONDARY_FULFILLMENT.toString()
      )
      .map((fulfillment) => ({
        ...fulfillment,
        selectedValue: fulfillment.id?.toString() || "",
        translatedName: fulfillment.name
          ? serverTranslate(fulfillment.name)
          : t("noData"),
      })),
    certificates: responseFilters.value.certificates?.map((certificate) => ({
      ...certificate,
      selectedValue: certificate.id.toString(),
      translatedName: certificate.name
        ? serverTranslate(certificate.name)
        : t("noData"),
    })),
    filterFaculties: filterFaculties.value
      ?.map((faculity) => ({
        ...faculity,
        selectedValue: faculity.id.toString(),
        translatedName: faculity.name
          ? serverTranslate(faculity.name)
          : t("noData"),
      }))
      .sort((a, b) => a.translatedName.localeCompare(b.translatedName)),
  };
});
const errorMsg: Ref<string> = ref("");

// Define Component Outputs (Emits)
const emit = defineEmits(["filters"]);

// On Mount Functions
const onQueryMount = async (event: { university: string }) => {
  await getReportsFilters();
  getFaculties(event);
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
const getFaculties = (event: { university: string }) => {
  filterFaculties.value = [];
  filterFaculties.value =
    responseFilters.value.faculties?.filter((faculty) => {
      return faculty.univ.toString() === event.university;
    }) || [];
};

// Provider Functions
const getReportsFilters = async () => {
  const filterResponse = await AcceptedStudentsNamesProvider.filters();
  responseFilters.value = filterResponse.payload;
  emit("filters", filterResponse.payload);
};

// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `reportsFiltersValidations.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

// Validation Rules
const rules = {
  university: {
    requiredUniversity: withI18nMessage(required),
  },
  year: {},
  faculty: {},
  studentStatus: {},
  region: {},
  semester: {},
  stage: {},
  registrationType: {},
  certificate: {},
  universityYear: {},
  gsYear: {},
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
