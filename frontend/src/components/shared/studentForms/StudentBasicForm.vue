<template>
  <div class="form-container">
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <InputText
          id="studentArName"
          class="w-full"
          type="text"
          :disabled="disableStatus"
          v-model="studentArName"
        />
        <label for="studentArName">{{ $t("studentArName") }}</label>
      </span>
      <small
        v-for="error of v$.studentArName.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <InputText
          id="studentEnName"
          class="w-full"
          type="text"
          :disabled="disableStatus"
          v-model="studentEnName"
        />
        <label for="studentEnName">{{ $t("studentEnName") }}</label>
      </span>
      <small
        v-for="error of v$.studentEnName.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="nationality"
          class="w-full"
          v-model="student.studentNationality_id"
          :options="translatedFormFilters.countries"
          :showClear="true"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          :disabled="disableStatus || (hasGSCertificate && !isIncoming)"
          optionLabel="translatedName"
          optionValue="id"
          @change="clearIds"
        />
        <label for="nationality">{{ $t("countryOfBirth") }} </label>
      </span>
    </div>
    <div
      class="field mt-3 mx-2"
      v-if="
        !student.studentNationality_id || student.studentNationality_id === 1
      "
    >
      <span class="p-float-label">
        <InputNumber
          id="nationalID"
          class="w-full"
          type="text"
          :useGrouping="false"
          :disabled="disableStatus || (hasGSCertificate && !isIncoming)"
          v-model="student.studentNID"
        />
        <label for="nationalID">{{ $t("nationalID") }}</label>
      </span>
      <small
        v-for="error of v$.student.studentNID.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2" v-else-if="student.studentNationality_id">
      <span class="p-float-label">
        <InputText
          id="studentPassport"
          class="w-full"
          type="text"
          :useGrouping="false"
          :disabled="disableStatus"
          v-model="student.studentPassport"
          @input="(event) => checkPassportInput(event)"
        />
        <label for="studentPassport">{{ $t("passport") }}</label>
      </span>
      <small
        v-for="error of v$.student.studentPassport.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <InputText
          v-if="
            !student.studentNationality_id ||
            student.studentNationality_id === 1
          "
          id="studentBirthDate"
          class="w-full"
          v-model="student.studentBirthDate"
          :disabled="
            disableStatus ||
            hasGSCertificate ||
            !student.studentNationality_id ||
            student.studentNationality_id === 1
          "
        />
        <Calendar
          v-else
          id="studentBirthDate"
          class="w-full p-no-today"
          panelClass="no-today-btn"
          :showIcon="true"
          :minDate="minBirthDate"
          :maxDate="maxBirthDate"
          :showButtonBar="true"
          :disabled="disableStatus"
          v-model="studentBirthDate"
          dateFormat="yy-mm-dd"
        />
        <label for="studentBirthDate">{{ $t("dateOfBirth") }} </label>
      </span>
      <small
        v-for="error of v$.student.studentBirthDate.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="gender"
          class="w-full"
          v-model="student.studentGender_id"
          :options="translatedFormFilters.genders"
          :showClear="true"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          :disabled="
            disableStatus ||
            hasGSCertificate ||
            !student.studentNationality_id ||
            student.studentNationality_id === 1
          "
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="gender">{{ $t("gender") }} </label>
      </span>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="placeOfBirth"
          class="w-full"
          v-model="student.studentBirthPlaceGov_id"
          :options="translatedFormFilters.governorates"
          :showClear="true"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          :disabled="disableStatus"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="placeOfBirth">{{ $t("placeOfBirth") }} </label>
      </span>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="religion"
          class="w-full"
          v-model="student.studentReligion_id"
          :options="translatedFormFilters.religions"
          :showClear="true"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          :disabled="disableStatus"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="religion">{{ $t("religion") }} </label>
      </span>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="residency"
          class="w-full"
          v-model="student.studentAddressPlaceGov_id"
          :options="translatedFormFilters.governorates"
          :showClear="true"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          :disabled="disableStatus"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="residency">{{ $t("residency") }} </label>
      </span>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <InputText
          id="studentAddress"
          class="w-full"
          :disabled="disableStatus"
          v-model="student.studentAddress"
        />
        <label for="studentAddress">{{ $t("address") }} </label>
      </span>
      <small
        v-for="error of v$.student.studentAddress.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <InputText
          id="studentPhone"
          class="w-full"
          :disabled="disableStatus"
          v-model="student.studentPhone"
        />
        <label for="studentPhone">{{ $t("phone") }} </label>
      </span>
      <small
        v-for="error of v$.student.studentPhone.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <InputText
          id="studentMail"
          type="email"
          class="w-full"
          :disabled="disableStatus"
          v-model="student.studentMail"
        />
        <label for="studentMail">{{ $t("emailInput") }} </label>
      </span>
      <small
        v-for="error of v$.student.studentMail.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <Dropdown
          id="residency"
          class="w-full"
          :filter="true"
          :filterFields="['translatedName', 'name']"
          v-model="student.studentStatus_id"
          :disabled="unselectableStatus"
          :options="translatedFormFilters.status"
          optionLabel="translatedName"
          optionValue="id"
        />
        <label for="notes">{{ $t("studentStatus") }} </label>
      </span>
      <small
        v-for="error of v$.student.studentStatus_id.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
  </div>
  <div class="container">
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <TextArea
          id="notes"
          :disabled="disableStatus"
          class="w-full"
          v-model="student.notes"
        />
        <label for="notes">{{ $t("notes") }} </label>
      </span>
      <small
        v-for="error of v$.student.notes.$errors"
        :key="error.$uid"
        class="p-error"
      >
        {{ error.$message }} <br />
      </small>
    </div>
  </div>
</template>

<script setup lang="ts">
import InputText from "primevue/inputtext";
import TextArea from "primevue/textarea";
import InputNumber from "primevue/inputnumber";
import Calendar from "primevue/calendar";
import Dropdown from "primevue/dropdown";
import { computed, onMounted, watch, type PropType } from "vue";
import {
  createI18nMessage,
  helpers,
  maxLength,
  required,
  type MessageProps,
} from "@vuelidate/validators";
import useVuelidate from "@vuelidate/core";
import { useI18n } from "vue-i18n";
import {
  CertificateEnum,
  CountryEnum,
  DateFormatPattern,
  EmailPattern,
  GenderEnum,
  IntegerPattern,
  NIDPattern,
  NoSymbolsPattern,
  RegistrationTypeEnum,
  StudentStatus,
} from "@/utils/enums";
import type { CouncilFilters, Status, Student } from "@/utils/types";
import { serverTranslate } from "@/utils/filters";

// Importing Services
const { t } = useI18n();

// Form Filters
const translatedFormFilters = computed(() => {
  return {
    genders: props.formFilters.genders?.map((gender) => ({
      ...gender,
      translatedName: gender.name ? serverTranslate(gender.name) : t("noData"),
    })),
    countries: props.formFilters.countries?.map((region) => ({
      ...region,
      translatedName: region.name ? serverTranslate(region.name) : t("noData"),
    })),
    religions: props.formFilters.religions?.map((religion) => ({
      ...religion,
      translatedName: religion.name
        ? serverTranslate(religion.name)
        : t("noData"),
    })),
    governorates: props.formFilters.governorates?.map((governorate) => ({
      ...governorate,
      translatedName: governorate.name
        ? serverTranslate(governorate.name)
        : t("noData"),
    })),
    status: filterStatus(
      props.formFilters.status?.map((status) => ({
        ...status,
        translatedName: status.name
          ? serverTranslate(status.name)
          : t("noData"),
      }))
    ),
  };
});
const minBirthDate = computed(() => {
  let date = new Date();
  date.setFullYear(1900);
  return date;
});
const maxBirthDate = computed(() => {
  let date = new Date();
  date.setFullYear(date.getFullYear() - 10);
  return date;
});
const disableStatus = computed(() => {
  return student.value.studentStatus_id === StudentStatus.INITIALLY_ACCEPTED;
});
const unselectableStatus = computed(() => {
  return [
    StudentStatus.TRANSFERRED,
    StudentStatus.GRADUATION_APPLICANT,
    StudentStatus.GRADUATE,
  ].includes(student.value.studentStatus_id || 0);
});
const hasGSCertificate = computed(() => {
  return (
    Boolean(props.studentOriginalNID) &&
    props.studentSecondaryCertId == CertificateEnum.EGYPTIAN_GENERAL_SECONADARY
  );
});
const isIncoming = computed(() => {
  return (
    props.studentRegistrationTypeId == RegistrationTypeEnum.INCOMING_STUDENTS
  );
});
const student = computed({
  get: () => props.student,
  set: (value) => emit("update:student", value),
});

// Define Component Inputs (Props)
const props = defineProps({
  isEdit: { type: Boolean, default: true },
  student: {
    type: Object as PropType<Student>,
    default: null,
  },
  studentOriginalNID: {
    type: Number,
    default: 0,
  },
  studentOriginalStatus: {
    type: Number,
    default: 0,
  },
  studentSecondaryCertId: {
    type: Number,
    default: 0,
  },
  studentRegistrationTypeId: {
    type: Number,
    default: 0,
  },
  formFilters: {
    type: Object as PropType<CouncilFilters>,
    default: null,
  },
});

// Define Component Outputs (Emits)
const emit = defineEmits(["update:student"]);

// Watchers
watch(
  () => [student.value.studentNID],
  () => setValuesFromNID(student.value.studentNID)
);

// Computed Student Data
const studentArName = computed({
  get() {
    return student.value.studentName?.split("|")[0] || "";
  },
  set(value: string) {
    student.value.studentName = value + "|" + studentEnName.value;
  },
});
const studentEnName = computed({
  get() {
    return student.value.studentName?.split("|")[1] || "";
  },
  set(value: string) {
    student.value.studentName = studentArName.value + "|" + value;
  },
});
const studentBirthDate = computed({
  get(): Date | undefined {
    if (student.value.studentBirthDate) {
      return new Date(student.value.studentBirthDate);
    }
    return undefined;
  },
  set(value: Date | undefined) {
    if (value) {
      const dd = String(value.getDate());
      const mm = String(value.getMonth() + 1); //January is 0!
      const yyyy = value.getFullYear();
      student.value.studentBirthDate = yyyy + "-" + mm + "-" + dd;
    } else {
      student.value.studentBirthDate = undefined;
    }
  },
});

// on mount functions
onMounted(async () => {
  if (props.isEdit) {
    await v$.value.$validate();
    if (student.value.studentNID) {
      setValuesFromNID(student.value.studentNID);
    }
  }
});

// Component Functions
const clearIds = () => {
  if (
    !isIncoming.value &&
    student.value.studentNationality_id &&
    student.value.studentNationality_id !== 1
  ) {
    student.value.studentPassport = undefined;
    student.value.studentNID = undefined;
  }
};

const filterStatus = (status?: Status[]) => {
  if (status && unselectableStatus.value) {
    return status;
  } else if (
    status &&
    [StudentStatus.WITHDRAWN].includes(props.studentOriginalStatus || 0)
  ) {
    return status.filter((status) =>
      [
        StudentStatus.ACCEPTED,
        StudentStatus.FULFILLMENT,
        StudentStatus.WITHDRAWN,
      ].includes(status.id)
    );
  } else if (status) {
    const notAllowedStatus = [
      StudentStatus.TRANSFERRED,
      StudentStatus.GRADUATION_APPLICANT,
      StudentStatus.GRADUATE,
    ];
    if (!props.isEdit) {
      notAllowedStatus.push(StudentStatus.INITIALLY_ACCEPTED);
    }
    return status.filter((status) => !notAllowedStatus.includes(status.id));
  }
  return [];
};

//sit data based on NID
const setValuesFromNID = (value?: number) => {
  const isValid = NIDPattern.test(value?.toString() || "");
  if (value && isValid) {
    let birthDate = "";
    if (value.toString().substr(0, 1) === "2") {
      birthDate += (1900 + Number(value.toString().substr(1, 2))).toString();
    } else {
      birthDate += (2000 + Number(value.toString().substr(1, 2))).toString();
    }
    if (value.toString().substr(3, 1) === "0") {
      birthDate += "-" + value.toString().substr(4, 1);
    } else {
      birthDate += "-" + value.toString().substr(3, 2);
    }
    if (value.toString().substr(5, 1) === "0") {
      birthDate += "-" + value.toString().substr(6, 1);
    } else {
      birthDate += "-" + value.toString().substr(5, 2);
    }
    if (Number(value.toString().substr(12, 1)) % 2 === 0) {
      student.value.studentGender_id = GenderEnum.FEMALE;
    } else {
      student.value.studentGender_id = GenderEnum.MALE;
    }
    student.value.studentBirthDate = birthDate;
  } else if (!value) {
    student.value.studentBirthDate = "";
  }
};

// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `addEditStudentValidations.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

// Custom Validators
const checkIntNumberType = helpers.regex(IntegerPattern);
const checkStudentNameText = helpers.regex(NoSymbolsPattern);
const checkDateText = helpers.regex(DateFormatPattern);
const checkEmailText = helpers.regex(EmailPattern);

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

const checkNameLength = (value: string, siblings: Student): boolean => {
  if (value && student.value.studentNationality_id === 1) {
    const nameLengthsArray = value.split(" ").map((w: string) => w.length);
    const filteredLengths = nameLengthsArray.filter(
      (value: number) => value > 0
    );
    if (
      siblings.studentNationality_id &&
      siblings.studentNationality_id !== CountryEnum.EGYPT
    ) {
      return filteredLengths.length > 1;
    }
    return filteredLengths.length > 3;
  }
  return true;
};

const checkNonEgyptiansNameLength = (value: string): boolean => {
  if (value && student.value.studentNationality_id !== 1) {
    const nameLengthsArray = value.split(" ").map((w: string) => w.length);
    const filteredLengths = nameLengthsArray.filter(
      (value: number) => value > 0
    );
    return filteredLengths.length >= 2;
  }
  return true;
};

const checkNID = (value: string, siblings: Student): boolean => {
  if (
    !props.isEdit &&
    (!siblings.studentNationality_id || siblings.studentNationality_id === 1)
  ) {
    return Boolean(value);
  }
  return true;
};
const checkNIDNumberLength = (value: string): boolean => {
  if (value) {
    return value.toString().length === 14 && Number.isInteger(Number(value));
  }
  return true;
};
const checkNIDNumber = (value: string, siblings: Student): boolean => {
  if (
    value &&
    (!siblings.studentNationality_id || siblings.studentNationality_id === 1)
  ) {
    return NIDPattern.test(value);
  }
  return true;
};
const checkPassportID = (value: string, siblings: Student): boolean => {
  if (
    !props.isEdit &&
    siblings.studentNationality_id &&
    siblings.studentNationality_id !== 1
  ) {
    return Boolean(value);
  }
  return true;
};
const checkBirthDateRange = (value: string): boolean => {
  if (value) {
    const dateValue = new Date(value);
    return maxBirthDate.value >= dateValue;
  }
  return true;
};

const checkPassportInput = (event: Event) => {
  if (
    event.target &&
    student.value.studentPassport &&
    student.value.studentPassport.includes(" ")
  ) {
    const targetInput = event.target as HTMLInputElement;
    const cursorPos = targetInput.selectionStart || 0;
    student.value.studentPassport = student.value.studentPassport.replace(
      /\s+/g,
      ""
    );
    targetInput.value = student.value.studentPassport;
    if (targetInput.value.length >= cursorPos - 1) {
      targetInput.selectionStart = targetInput.selectionEnd = cursorPos - 1;
    }
  }
};

// Validation Rules
const rules = {
  studentArName: {
    checkName: withI18nMessage(required),
    requiredStudentEachNameLength: withI18nMessage(checkEachNameLength),
    requiredStudentNameLength: withI18nMessage(checkNameLength),
    requiredStudentQuadNameLength: withI18nMessage(checkNonEgyptiansNameLength),
    textFieldMaxLength: withI18nMessage(maxLength(127)),
    checkStudentNameText: withI18nMessage(checkStudentNameText),
  },
  studentEnName: {
    requiredStudentEachNameLength: withI18nMessage(checkEachNameLength),
    requiredStudentNameLength: withI18nMessage(checkNameLength),
    requiredStudentQuadNameLength: withI18nMessage(checkNonEgyptiansNameLength),
    textFieldMaxLength: withI18nMessage(maxLength(127)),
    checkStudentNameText: withI18nMessage(checkStudentNameText),
  },
  student: {
    studentNID: {
      checkNID: withI18nMessage(checkNID),
      checkNIDNumberLength: withI18nMessage(checkNIDNumberLength),
      checkNIDNumber: withI18nMessage(checkNIDNumber),
    },
    studentPassport: {
      checkPassport: withI18nMessage(checkPassportID),
      checkPassportLength: withI18nMessage(maxLength(20)),
    },
    studentBirthDate: {
      checkDateFormat: withI18nMessage(checkDateText),
      checkDateRange: withI18nMessage(checkBirthDateRange),
    },
    studentAddress: {
      textFieldMaxLength: withI18nMessage(maxLength(200)),
    },
    studentPhone: {
      checkPhone: withI18nMessage(checkIntNumberType),
      fieldMaxLength: withI18nMessage(maxLength(20)),
    },
    studentMail: {
      checkEmail: withI18nMessage(checkEmailText),
      textFieldMaxLength: withI18nMessage(maxLength(75)),
    },
    studentStatus_id: {
      checkStatus: withI18nMessage(required),
    },
    notes: {
      textFieldMaxLength: withI18nMessage(maxLength(500)),
    },
  },
};

// Set up component Validation
const v$ = useVuelidate(rules, {
  student,
  studentArName,
  studentEnName,
});
</script>

<style scoped lang="scss"></style>
