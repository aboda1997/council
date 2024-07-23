<template>
  <div class="form-container">
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="certificate"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentSecondaryEdu.studentSecondaryCert_id"
          :options="translatedFormFilters.certificates"
          :disabled="disableStatus || (props.isEdit && hasGSCertificate)"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="certificate">{{ $t("certificate") }} </label>
      </span>
      <small
        v-for="error of v$.studentSecondaryEdu.studentSecondaryCert_id.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="certYear"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentSecondaryEdu.studentCertificateYear_id"
          :options="translatedFormFilters.certyears"
          :disabled="disableStatus || (props.isEdit && hasGSCertificate)"
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
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="studyGroup"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentSecondaryEdu.studentStudyGroup_id"
          :options="translatedFormFilters.studyGroups"
          :disabled="disableStatus || (props.isEdit && hasGSCertificate)"
          :showClear="true"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="studyGroup">{{ $t("studyGroup") }} </label>
      </span>
      <small
        v-for="error of v$.studentSecondaryEdu.studentStudyGroup_id.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <InputNumber
          id="studentTot"
          class="w-full"
          type="text"
          :useGrouping="false"
          :minFractionDigits="0"
          :maxFractionDigits="3"
          v-model="studentSecondaryEdu.studentTot"
          :disabled="disableStatus || (props.isEdit && hasGSCertificate)"
        />
        <label for="studentTot">{{ $t("totalGrade") }}</label>
      </span>
      <small
        v-for="error of v$.studentSecondaryEdu.studentTot.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div
      class="field mt-3 mx-2"
      v-if="studentSecondaryEdu.studentSecondaryCert_id !== gsCertId"
    >
      <span class="p-float-label">
        <InputNumber
          id="studentTot"
          class="w-full"
          type="text"
          :useGrouping="false"
          :minFractionDigits="0"
          :maxFractionDigits="3"
          :disabled="disableStatus"
          v-model="studentSecondaryEdu.studentEquivTot"
        />
        <label for="studentTot">{{ $t("totalGradeEquivalent") }}</label>
      </span>
      <small
        v-for="error of v$.studentSecondaryEdu.studentEquivTot.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div v-if="hasGSCertificate" class="field mt-3 mx-2">
      <span class="p-float-label">
        <InputNumber
          id="studentSportDegree"
          class="w-full"
          type="text"
          :useGrouping="false"
          :minFractionDigits="0"
          :maxFractionDigits="3"
          :disabled="disableStatus"
          v-model="studentSecondaryEdu.studentSportDegree"
        />
        <label for="studentSportDegree">{{ $t("studentSportDegree") }}</label>
      </span>
      <small
        v-for="error of v$.studentSecondaryEdu.studentSportDegree.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div v-if="hasGSCertificate" class="field mt-3 mx-2">
      <span class="p-float-label">
        <InputNumber
          id="studentComplainGain"
          class="w-full"
          type="text"
          :useGrouping="false"
          :minFractionDigits="0"
          :maxFractionDigits="3"
          :disabled="disableStatus"
          v-model="studentSecondaryEdu.studentComplainGain"
        />
        <label for="studentComplainGain">{{
          $t("studentComplainGainDegree")
        }}</label>
      </span>
      <small
        v-for="error of v$.studentSecondaryEdu.studentComplainGain.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <InputNumber
          id="totalGradePercentage"
          class="w-full"
          type="text"
          suffix="%"
          :useGrouping="false"
          :disabled="true"
          v-model="studentDegreePercentage"
        />
        <label for="totalGradePercentage">{{
          $t("totalGradePercentage")
        }}</label>
      </span>
    </div>
    <div v-if="hasGSCertificate" class="field mt-3 mx-2">
      <span class="p-float-label">
        <InputNumber
          id="seatNumber"
          class="w-full"
          :useGrouping="false"
          v-model="studentSecondaryEdu.studentSeatNumber"
          :disabled="disableStatus || props.isEdit"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="seatNumber">{{ $t("seatNumber") }} </label>
      </span>
      <small
        v-for="error of v$.studentSecondaryEdu.studentSeatNumber.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="fulFillment"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="studentSecondaryEdu.studentFulfillment_id"
          :options="translatedFormFilters.fulfillments"
          :showClear="true"
          :disabled="disableStatus || !hasFulfillmentStatus"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="fulFillment">{{ $t("fulFillment") }} </label>
      </span>
      <small
        v-for="error of v$.studentSecondaryEdu.studentFulfillment_id.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
  </div>
</template>

<script setup lang="ts">
import InputNumber from "primevue/inputnumber";
import Dropdown from "primevue/dropdown";
import { computed, onMounted, type PropType } from "vue";
import {
  createI18nMessage,
  helpers,
  type MessageProps,
} from "@vuelidate/validators";
import useVuelidate from "@vuelidate/core";
import { useI18n } from "vue-i18n";
import {
  CertificateEnum,
  Float3DigitPattern,
  FulfillmentTypeEnum,
  StudentStatus,
} from "@/utils/enums";
import type { CouncilFilters, StudentSecondaryEdu, Years } from "@/utils/types";
import { serverTranslate } from "@/utils/filters";

// Static Variables
const totalDegree = 410;
const gsCertId = 1;

// Importing Services
const { t } = useI18n();

// Form Filters
const translatedFormFilters = computed(() => {
  return {
    certificates: props.formFilters.certificates
      ?.filter((certificate) => {
        if (
          props.isEdit &&
          studentSecondaryEdu.value &&
          studentSecondaryEdu.value.studentSecondaryCert_id !== gsCertId
        ) {
          return certificate.id !== gsCertId;
        }
        return true;
      })
      .map((certificate) => ({
        ...certificate,
        translatedName: certificate.name
          ? serverTranslate(certificate.name)
          : t("noData"),
      })),
    certyears: filterCurrentYears(
      props.formFilters.years?.map((year) => ({
        ...year,
        translatedName: year.name ? serverTranslate(year.name) : t("noData"),
      }))
    ),
    studyGroups: props.formFilters.studyGroups?.map((studyGroup) => ({
      ...studyGroup,
      translatedName: studyGroup.name
        ? serverTranslate(studyGroup.name)
        : t("noData"),
    })),
    fulfillments: props.formFilters.fulfillments
      ?.filter(
        (fulfillment) =>
          fulfillment.typeid ==
          FulfillmentTypeEnum.SECONDARY_FULFILLMENT.toString()
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
const studentDegreePercentage = computed(() => {
  if (
    studentSecondaryEdu.value &&
    studentSecondaryEdu.value.studentSecondaryCert_id === gsCertId &&
    studentSecondaryEdu.value.studentTot
  ) {
    let sportDegree = studentSecondaryEdu.value.studentSportDegree || 0;
    let complainGainDegree = studentSecondaryEdu.value.studentComplainGain || 0;
    let total =
      +Number(studentSecondaryEdu.value.studentTot) +
      +Number(sportDegree) +
      +Number(complainGainDegree);
    return Math.round(((total * 100) / totalDegree) * 100) / 100;
  } else if (studentSecondaryEdu.value?.studentEquivTot) {
    return (
      Math.round(
        ((studentSecondaryEdu.value.studentEquivTot * 100) / totalDegree) * 100
      ) / 100
    );
  }
  return undefined;
});
const disableStatus = computed(() => {
  return props.studentStatusId == StudentStatus.INITIALLY_ACCEPTED;
});
const hasFulfillmentStatus = computed(() => {
  return props.studentStatusId == StudentStatus.FULFILLMENT;
});
const hasGSCertificate = computed(() => {
  return (
    studentSecondaryEdu.value.studentSecondaryCert_id ==
    CertificateEnum.EGYPTIAN_GENERAL_SECONADARY
  );
});
const studentSecondaryEdu = computed({
  get: () => props.studentSecondaryEdu,
  set: (value) => emit("update:studentSecondaryEdu", value),
});

// Define Component Inputs (Props)
const props = defineProps({
  isEdit: { type: Boolean, default: true },
  studentStatusId: {
    type: Number,
    default: -1,
  },
  studentSecondaryEdu: {
    type: Object as PropType<StudentSecondaryEdu>,
    default: null,
  },
  formFilters: {
    type: Object as PropType<CouncilFilters>,
    default: null,
  },
});

// Define Component Outputs (Emits)
const emit = defineEmits(["update:studentSecondaryEdu"]);

// on mount functions
onMounted(async () => {
  if (props.isEdit) {
    await v$.value.$validate();
  }
});

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

// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `addEditStudentValidations.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

// Custom Validators
const checkFloatNumberType = helpers.regex(Float3DigitPattern);

const checkTotalDegreeRequired = (value: TemplateStringsArray): boolean => {
  if (
    studentSecondaryEdu.value &&
    studentSecondaryEdu.value.studentSecondaryCert_id &&
    studentSecondaryEdu.value.studentSecondaryCert_id ==
      CertificateEnum.EGYPTIAN_GENERAL_SECONADARY
  ) {
    return Boolean(value.toString());
  }
  return true;
};

const checkTotalEquivDegreeRequired = (
  value: TemplateStringsArray
): boolean => {
  if (
    studentSecondaryEdu.value &&
    studentSecondaryEdu.value.studentSecondaryCert_id &&
    studentSecondaryEdu.value.studentSecondaryCert_id !==
      CertificateEnum.EGYPTIAN_GENERAL_SECONADARY
  ) {
    return Boolean(value.toString());
  }
  return true;
};

const checkStudentFulfillment = (value: TemplateStringsArray) => {
  if (hasFulfillmentStatus.value) {
    return Boolean(value);
  }
  return true;
};

const checkRequiredOnAdd = (value: TemplateStringsArray) => {
  if (!props.isEdit) {
    return Boolean(value);
  }
  return true;
};

const checkMaxLengthSeatNumber = (value: TemplateStringsArray) => {
  if (!props.isEdit) {
    return String(value).length <= 9;
  }
  return true;
};
// Validation Rules
const rules = {
  studentSecondaryEdu: {
    studentSecondaryCert_id: {
      checkCertificate: withI18nMessage(checkRequiredOnAdd),
    },
    studentCertificateYear_id: {
      checkCertificateYear: withI18nMessage(checkRequiredOnAdd),
    },
    studentStudyGroup_id: {
      checkStudyGroup: withI18nMessage(checkRequiredOnAdd),
    },
    studentTot: {
      checkTotalGrades: withI18nMessage(checkTotalDegreeRequired),
      checkNumberType: withI18nMessage(checkFloatNumberType),
    },
    studentEquivTot: {
      checkEquivTotalGrades: withI18nMessage(checkTotalEquivDegreeRequired),
      checkNumberType: withI18nMessage(checkFloatNumberType),
    },
    studentSportDegree: {
      checkNumberType: withI18nMessage(checkFloatNumberType),
    },
    studentComplainGain: {
      checkNumberType: withI18nMessage(checkFloatNumberType),
    },
    studentFulfillment_id: {
      checkStudentFulfillment: withI18nMessage(checkStudentFulfillment),
    },
    studentSeatNumber: {
      seatNumberMaxLength: withI18nMessage(checkMaxLengthSeatNumber),
    },
  },
};

// Set up component Validation
const v$ = useVuelidate(rules, {
  studentSecondaryEdu,
});
</script>

<style scoped lang="scss"></style>
