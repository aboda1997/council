<template>
  <SearchFilters
    :rules="rules"
    :errorMsg="errorMsg"
    :initQuery="props.initQuery"
    :filters="translatedFilters"
    :advancedSearchFields="props.advancedSearchFields"
    @queryMounted="onQueryMount"
  >
    <template
      v-if="props.simpleSearchFields && props.simpleSearchFields.length"
      #simplefields="slotProps"
    >
      <div class="grid-container" :class="props.simpleSearchFieldsClasses">
        <div
          v-if="canDisplaySimpleField('selectedStudentType')"
          class="field px-2 m-0 mt-4 flex"
        >
          <div class="field-radiobutton my-auto">
            <RadioButton
              id="type1"
              name="type"
              :value="studentType[0].type"
              v-model="slotProps.query.selectedStudentType"
            />
            <label for="type1">{{ $t("student") }}</label>
          </div>
          <div
            v-if="
              canDisplaySimpleField('selectedStudentType') &&
              canDisplaySimpleField('studentStatus') &&
              slotProps.query.selectedStudentType === 'student'
            "
            class="field px-2 m-0 flex-grow-1"
          >
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
        </div>
        <div
          v-if="canDisplaySimpleField('selectedStudentType')"
          class="field px-2 m-0 mt-4 flex"
        >
          <div class="field-radiobutton my-auto">
            <RadioButton
              id="type2"
              name="type"
              :value="studentType[1].type"
              v-model="slotProps.query.selectedStudentType"
              @change="slotProps.clearField('studentStatus')"
            />
            <label for="type2">{{ $t("graduate") }}</label>
          </div>
        </div>
        <div
          v-if="
            !canDisplaySimpleField('selectedStudentType') &&
            canDisplaySimpleField('studentStatus')
          "
          class="field px-2 m-0 mt-4"
        >
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
            canDisplaySimpleField('nationalID') &&
            (!slotProps.query.region ||
              (slotProps.query.region === '1' && slotProps.query.region))
          "
          class="field px-2 m-0 mt-4"
        >
          <span class="p-float-label">
            <InputNumber
              id="nationalID"
              class="w-full"
              type="text"
              v-model="slotProps.query.nationalID"
              :value="
                slotProps.query.nationalID ? slotProps.query.nationalID : ''
              "
              :useGrouping="false"
            />
            <label for="nationalID">{{ $t("nationalID") }}</label>
          </span>
          <small
            v-for="error of slotProps.v$.nationalID.$errors"
            :key="error.$uid"
            class="p-error"
          >
            {{ error.$message }} <br />
          </small>
        </div>
        <div
          v-if="canDisplaySimpleField('studentName')"
          class="field px-2 m-0 mt-4"
        >
          <span class="p-float-label">
            <InputText
              id="studentName"
              class="w-full"
              type="text"
              @input="
                studentNameInput(slotProps.query.studentName, slotProps.query)
              "
              v-model="slotProps.query.studentName"
            />
            <label for="studentName">{{ $t("studentName") }}</label>
          </span>
          <small
            v-for="error of slotProps.v$.studentName.$errors"
            :key="error.$uid"
            class="p-error"
          >
            {{ error.$message }} <br />
          </small>
        </div>
      </div>
    </template>
    <template
      v-if="props.advancedSearchFields && props.advancedSearchFields.length"
      #advancedfields="slotProps"
    >
      <div class="grid-container" :class="props.advancedSearchFieldsClasses">
        <div
          v-if="
            canDisplayAdvancedField('fulfillment') &&
            slotProps.query.studentStatus &&
            slotProps.query.studentStatus === '3'
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
        <div
          v-if="canDisplayAdvancedField('region')"
          class="field px-2 m-0 mt-4"
        >
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
        <div
          v-if="
            canDisplayAdvancedField('passport') &&
            slotProps.query.region !== '1' &&
            slotProps.query.region
          "
          class="field px-2 m-0 mt-4"
        >
          <span class="p-float-label">
            <InputText
              id="passport"
              class="w-full"
              type="text"
              v-model="slotProps.query.passport"
            />
            <label for="passport">{{ $t("passport") }}</label>
          </span>
          <small
            v-for="error of slotProps.v$.passport.$errors"
            :key="error.$uid"
            class="p-error"
          >
            {{ error.$message }} <br />
          </small>
        </div>
        <div
          v-if="canDisplayAdvancedField('certificate')"
          class="field px-2 m-0 mt-4"
        >
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
        <div
          v-if="
            canDisplayAdvancedField('seatNumber') &&
            slotProps.query.certificate === '1' &&
            slotProps.query.certificate
          "
          class="field px-2 m-0 mt-4"
        >
          <span class="p-float-label">
            <InputText
              id="passport"
              class="w-full"
              type="text"
              v-model="slotProps.query.seatNumber"
            />
            <label for="passport">{{ $t("seatNumber") }}</label>
          </span>
          <small
            v-for="error of slotProps.v$.seatNumber.$errors"
            :key="error.$uid"
            class="p-error"
          >
            {{ error.$message }} <br />
          </small>
        </div>
        <div
          v-if="
            canDisplayAdvancedField('gsYear') && slotProps.query.certificate
          "
          class="field px-2 m-0 mt-4"
        >
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
        <div
          v-if="canDisplayAdvancedField('registrationType')"
          class="field px-2 m-0 mt-4"
        >
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
        <div
          v-if="canDisplayAdvancedField('university')"
          class="field px-2 m-0 mt-4"
        >
          <span class="p-float-label">
            <Dropdown
              id="university"
              class="w-full"
              v-model="slotProps.query.university"
              :options="slotProps.filters.universities"
              :showClear="Boolean(slotProps.query.university)"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              optionLabel="translatedName"
              optionValue="selectedValue"
              @change="
                getFaculties(slotProps.query);
                slotProps.clearField('faculty');
              "
            />
            <label for="university">{{ $t("university") }} </label>
          </span>
        </div>
        <div
          v-if="canDisplayAdvancedField('faculty')"
          class="field px-2 m-0 mt-4"
        >
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
        <div
          v-if="canDisplayAdvancedField('universityYear')"
          class="field px-2 m-0 mt-4"
        >
          <span class="p-float-label">
            <Dropdown
              id="enrollYear"
              class="w-full"
              v-model="slotProps.query.universityYear"
              :options="slotProps.filters.universityYear"
              :showClear="Boolean(slotProps.query.universityYear)"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              optionLabel="translatedName"
              optionValue="selectedValue"
            />
            <label for="enrollYear"
              >{{ $t("universityEnrollmentYear") }}
            </label>
          </span>
        </div>
        <div
          v-if="canDisplayAdvancedField('semester')"
          class="field px-2 m-0 mt-4"
        >
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

        <div
          v-if="canDisplayAdvancedField('stage')"
          class="field px-2 m-0 mt-4"
        >
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
        <div
          v-if="canDisplayAdvancedField('militaryStatusType')"
          class="field px-2 m-0 mt-4"
        >
          <span class="p-float-label">
            <Dropdown
              id="militaryEduStatus"
              class="w-full"
              v-model="slotProps.query.militaryStatusType"
              :options="slotProps.filters.militaryStatusTypes"
              :showClear="Boolean(slotProps.query.militaryStatusType)"
              :filter="true"
              :filterFields="['translatedName', 'name']"
              optionLabel="translatedName"
              optionValue="name"
            />
            <label for="militaryEduStatus">{{ $t("militaryEduStatus") }}</label>
          </span>
        </div>
      </div>
    </template>
  </SearchFilters>
</template>
<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import RadioButton from "primevue/radiobutton";
import Dropdown from "primevue/dropdown";
import InputText from "primevue/inputtext";
import InputNumber from "primevue/inputnumber";
import SearchFilters from "./SearchFilters.vue";
import { type Ref, ref, computed, type PropType } from "vue";
import { useI18n } from "vue-i18n";
import {
  createI18nMessage,
  maxLength,
  type MessageProps,
} from "@vuelidate/validators";
import {
  FulfillmentTypeEnum,
  IntegerPattern,
  MilitaryStatusType,
  NIDPattern,
  NoSymbolsPattern,
} from "@/utils/enums";
import type {
  BasicAttribute,
  CouncilFilters,
  Faculty,
  Years,
} from "@/utils/types";
import { SymbolsPattern } from "@/utils/enums";
import { serverTranslate } from "@/utils/filters";

// Importing Services
const { t } = useI18n();

// Fixed Values
const studentType = ref([{ type: "student" }, { type: "graduate" }]);
const militaryStatusTypes: BasicAttribute[] = [
  { name: MilitaryStatusType.NOT_PERFORMED },
  { name: MilitaryStatusType.PERFORMED },
];

// Dynamic Values
const filters: Ref<CouncilFilters> = ref({});
const translatedFilters: Ref<CouncilFilters> = computed(() => {
  return {
    ...filters.value,
    universityYear: filterCurrentYears(
      filters.value.years?.map((year) => ({
        ...year,
        selectedValue: year.id.toString(),
        translatedName: year.name ? serverTranslate(year.name) : t("noData"),
      })),
      true
    ),
    gsYear: filterCurrentYears(
      filters.value.years?.map((year) => ({
        ...year,
        selectedValue: year.id.toString(),
        translatedName: year.name ? serverTranslate(year.name) : t("noData"),
      })),
      false
    ),
    registrationTypes: filters.value.registrationTypes?.map(
      (registrationType) => ({
        ...registrationType,
        selectedValue: registrationType.id.toString(),
        translatedName: registrationType.name
          ? serverTranslate(registrationType.name)
          : t("noData"),
      })
    ),
    universities: filters.value.universities
      ?.map((university) => ({
        ...university,
        selectedValue: university.id.toString(),
        translatedName: university.name
          ? serverTranslate(university.name)
          : t("noData"),
      }))
      .sort((a, b) => a.translatedName.localeCompare(b.translatedName)),
    status: filters.value.status?.map((status) => ({
      ...status,
      selectedValue: status.id.toString(),
      translatedName: status.name ? serverTranslate(status.name) : t("noData"),
    })),
    regions: filters.value.countries
      ?.map((region) => ({
        ...region,
        selectedValue: region.id.toString(),
        translatedName: region.name
          ? serverTranslate(region.name)
          : t("noData"),
      }))
      .sort((a, b) => a.translatedName.localeCompare(b.translatedName)),
    semesters: filters.value.semesters?.map((semester) => ({
      ...semester,
      selectedValue: semester.id.toString(),
      translatedName: semester.name
        ? serverTranslate(semester.name)
        : t("noData"),
    })),
    stages: filters.value.stages?.map((stage) => ({
      ...stage,
      selectedValue: stage.id.toString(),
      translatedName: stage.name ? serverTranslate(stage.name) : t("noData"),
    })),
    fulfillments: filters.value.fulfillments
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
    certificates: filters.value.certificates?.map((certificate) => ({
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
    militaryStatusTypes: militaryStatusTypes.map((type) => ({
      ...type,
      translatedName: type.name ? t(type.name) : t("noData"),
    })),
  };
});

const filterFaculties: Ref<Faculty[]> = ref([]);
const errorMsg: Ref<string> = ref("");

// Define Component Inputs (Props)
const props = defineProps({
  provider: { type: Object as PropType<any> },
  initQuery: {
    type: Object as PropType<any>,
    default: () => {
      return { selectedStudentType: "student" };
    },
  },
  simpleSearchFields: {
    type: Array,
    default: () => ["*"],
  },
  simpleSearchFieldsClasses: {
    type: String,
    default: () => "",
  },
  advancedSearchFields: {
    type: Array,
    default: () => ["*"],
  },
  advancedSearchFieldsClasses: {
    type: String,
    default: () => "",
  },
});

// On Mount Function
const onQueryMount = async (event: { university: string }) => {
  if (!props.provider) {
    errorMsg.value = "Missing `provider` prop for StudentFilter Component";
  } else {
    await getCouncilFilters();
    getFaculties(event);
  }
};

// Component Functions
const canDisplaySimpleField = (key: string) => {
  return (
    props.simpleSearchFields.includes("*") ||
    props.simpleSearchFields.includes(key)
  );
};
const canDisplayAdvancedField = (key: string) => {
  return (
    props.simpleSearchFields.includes("*") ||
    props.advancedSearchFields.includes(key)
  );
};
const getCouncilFilters = async () => {
  const filterResponse = await props.provider.filters();
  filters.value = filterResponse.payload;
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

const getFaculties = (event: { university: string }) => {
  filterFaculties.value = [];
  filterFaculties.value =
    filters.value.faculties?.filter((faculty) => {
      return faculty.univ.toString() === event.university;
    }) || [];
};

// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `inqueryFiltersValidations.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

//student name inputtext validation
const studentNameInput = (
  studentName: string,
  query: { studentName: string }
) => {
  query.studentName = studentName.replace(SymbolsPattern, "");
};
// Form Validation Rules
const checkEachNameLength = (value: string): boolean => {
  if (value) {
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

const checkNameLength = (value: string): boolean => {
  if (value) {
    const nameLengthsArray = value.split(" ").map((w: string) => w.length);
    const filteredLengths = nameLengthsArray.filter(
      (value: number) => value > 0
    );
    return filteredLengths.length > 1;
  }
  return true;
};

const checkTotalNameLength = (value: string): boolean => {
  if (value) {
    return value.length <= 100;
  }
  return true;
};

const checkStudentNameText = (value: string): boolean => {
  if (value) {
    return NoSymbolsPattern.test(value);
  }
  return true;
};
const checkNIDNumberLength = (value: string): boolean => {
  if (value) {
    return value.toString().length === 14 && Number.isInteger(Number(value));
  }
  return true;
};
const checkNIDNumber = (value: string): boolean => {
  if (value) {
    return NIDPattern.test(value);
  }
  return true;
};
const checkSeatNumberLength = (value: string): boolean => {
  if (value) {
    return value.length <= 9;
  }
  return true;
};
const checkInteger = (value: string): boolean => {
  if (value) {
    return IntegerPattern.test(value);
  }
  return true;
};

// Validation Rules
const rules = {
  nationalID: {
    checkNIDNumber: withI18nMessage(checkNIDNumber),
    checkNIDNumberLength: withI18nMessage(checkNIDNumberLength),
  },
  studentName: {
    requiredStudentNameLength: withI18nMessage(checkNameLength),
    requiredStudentEachNameLength: withI18nMessage(checkEachNameLength),
    requiredStudentNameFullLength: withI18nMessage(checkTotalNameLength),
    checkStudentNameText: withI18nMessage(checkStudentNameText),
  },
  passport: {
    checkPassportLength: withI18nMessage(maxLength(20)),
  },
  seatNumber: {
    checkInteger: withI18nMessage(checkInteger),
    checkSeatNumberLength: withI18nMessage(checkSeatNumberLength),
  },
  faculty: {},
  studentStatus: {},
  region: {},
  semester: {},
  stage: {},
  registrationType: {},
  certificate: {},
  university: {},
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
