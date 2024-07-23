<template>
  <PageLoader
    v-if="isLoading || errorMessage"
    :loading="isLoading"
    :error="errorMessage"
  />
  <template v-else>
    <form @submit.prevent="submitStudentForm" form="AddEditCDStudentForm">
      <div class="flex flex-column">
        <div
          class="header grid justify-content-between p-2 md:flex-row flex-column-reverse"
        >
          <h4 class="mt-3 mb-0 mx-3">{{ $t("studentData") }}</h4>
          <div class="button-wrapper flex md:mt-2">
            <Button
              :label="$t('cancel')"
              class="p-button p-button-secondary p-button-sm flex-grow-1 mx-2 my-auto"
              @click="cancel()"
            />
          </div>
        </div>

        <div class="form-container">
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputText
                id="studentName"
                class="w-full"
                type="text"
                v-model="student.arabic_name"
              />
              <label for="studentName">{{ $t("studentName") }}</label>
            </span>
            <small
              v-for="error of v$.student.arabic_name.$errors"
              :key="error.$uid"
              class="p-error"
            >
              {{ error.$message }} <br />
            </small>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputText
                id="nationalID"
                class="w-full"
                type="number"
                v-model="student.national_no"
                :disabled="!props.isEdit"
                @blur="setValuesFromNID"
              />
              <label for="nationalID">{{ $t("nationalID") }}</label>
            </span>
            <small
              v-for="error of v$.student.national_no.$errors"
              :key="error.$uid"
              class="p-error"
            >
              {{ error.$message }} <br />
            </small>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputNumber
                id="seatNumber"
                class="w-full"
                type="text"
                :useGrouping="false"
                v-model="student.seating_no"
              />
              <label for="seatNumber">{{ $t("seatNumber") }}</label>
            </span>
            <small
              v-for="error of v$.student.seating_no.$errors"
              :key="error.$uid"
              class="p-error"
            >
              {{ error.$message }} <br />
            </small>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputNumber
                id="tansiqNumber"
                class="w-full"
                type="text"
                :useGrouping="false"
                v-model="student.tanseq_number"
              />
              <label for="tansiqNumber">{{ $t("tansiqNumber") }}</label>
            </span>
            <small
              v-for="error of v$.student.tanseq_number.$errors"
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
                v-model="student.nationality"
                :options="gsFilters.nationalityList"
                :showClear="true"
                optionLabel="nationality_name"
                optionValue="nationality_code"
              />
              <label for="nationality">{{ $t("nationality") }} </label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="religion"
                class="w-full"
                v-model="student.religion_id"
                :options="gsFilters.studentReligionList"
                :showClear="true"
                optionLabel="religion_name"
                optionValue="religion_code"
              />
              <label for="religion">{{ $t("religion") }} </label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="gender"
                class="w-full"
                v-model="student.gender_id"
                :options="gsFilters.studentGenderList"
                :showClear="true"
                optionLabel="gender_name"
                optionValue="gender_code"
              />
              <label for="gender">{{ $t("gender") }} </label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputText
                id="dateOfBirth"
                class="w-full"
                v-model="student.date_of_birth"
                :disabled="true"
              />
              <label for="dateOfBirth">{{ $t("dateOfBirth") }} </label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="placeOfBirth"
                class="w-full"
                v-model="student.birth_palace"
                :options="gsFilters.governorates"
                :showClear="true"
                optionLabel="governorate_name"
                optionValue="governorate_name"
              />
              <label for="placeOfBirth">{{ $t("placeOfBirth") }} </label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputText
                id="barCode"
                class="w-full"
                type="text"
                v-model="student.bar_code"
              />
              <label for="barCode">{{ $t("barCode") }}</label>
            </span>
            <small
              v-for="error of v$.student.bar_code.$errors"
              :key="error.$uid"
              class="p-error"
            >
              {{ error.$message }} <br />
            </small>
          </div>
        </div>
        <h4 class="mt-1 mb-3 mx-3">{{ $t("residency") }}</h4>
        <div class="form-container">
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="addressGovernorate"
                class="w-full"
                v-model="student.city_code"
                :options="gsFilters.governorates"
                :showClear="true"
                optionLabel="governorate_name"
                optionValue="governorate_code"
              />
              <label for="addressGovernorate">{{ $t("residency") }} </label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputText
                id="policeStation"
                class="w-full"
                v-model="student.police_station"
              />
              <label for="policeStation">{{ $t("policeStation") }} </label>
            </span>
            <small
              v-for="error of v$.student.police_station.$errors"
              :key="error.$uid"
              class="p-error"
            >
              {{ error.$message }} <br />
            </small>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputText
                id="address"
                class="w-full"
                v-model="student.address"
              />
              <label for="address">{{ $t("address") }} </label>
            </span>
            <small
              v-for="error of v$.student.address.$errors"
              :key="error.$uid"
              class="p-error"
            >
              {{ error.$message }} <br />
            </small>
          </div>
        </div>
        <h4 class="mt-1 mb-3 mx-3">{{ $t("eduData") }}</h4>
        <div class="form-container">
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="branch"
                class="w-full"
                v-model="student.branch_code_new"
                :options="gsFilters.studentsBranchList"
                :showClear="true"
                @change="setStudentBranchFlags"
                optionLabel="branch_name"
                optionValue="branch_code_str"
              />
              <label for="branch">{{ $t("branch") }} </label>
            </span>
            <small
              v-for="error of v$.student.branch_code_new.$errors"
              :key="error.$uid"
              class="p-error"
            >
              {{ error.$message }} <br />
            </small>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="educationType"
                class="w-full"
                v-model="student.school_code"
                :options="gsFilters.schoolCodeList"
                :showClear="true"
                optionLabel="school_name"
                optionValue="school_code"
              />
              <label for="educationType">{{ $t("educationType") }} </label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="schoolType"
                class="w-full"
                v-model="student.school_type_id"
                :options="gsFilters.schoolTypeList"
                :showClear="true"
                optionLabel="school_type_name"
                optionValue="school_type_code"
              />
              <label for="schoolType">{{ $t("schoolType") }} </label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="moderia"
                class="w-full"
                v-model="student.moderia"
                :options="gsFilters.governorates"
                :showClear="true"
                optionLabel="governorate_name"
                optionValue="governorate_code"
                @change="filterAdminstrations(true)"
              />
              <label for="moderia">{{ $t("moderia") }} </label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="adminstrationName"
                class="w-full"
                v-model="student.dept_code"
                :options="filteredGSFilters.educationalAdministrations"
                :showClear="true"
                optionLabel="edu_admin_name"
                optionValue="edu_admin_code"
              />
              <label for="adminstrationName"
                >{{ $t("adminstrationName") }}
              </label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputText
                id="schoolName"
                class="w-full"
                type="text"
                v-model="student.school_name"
              />
              <label for="schoolName">{{ $t("schoolName") }}</label>
            </span>
            <small
              v-for="error of v$.student.school_name.$errors"
              :key="error.$uid"
              class="p-error"
            >
              {{ error.$message }} <br />
            </small>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="control"
                class="w-full"
                v-model="student.control_code"
                :options="gsFilters.controlList"
                :showClear="true"
                optionLabel="control_name"
                optionValue="control_code"
              />
              <label for="control">{{ $t("control") }} </label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="firstLanguage"
                class="w-full"
                v-model="student.lang_1"
                :options="gsFilters.languagesList"
                :showClear="true"
                optionLabel="lang_name"
                optionValue="lang_code_str"
              />
              <label for="firstLanguage">{{ $t("firstLanguage") }} </label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="secondLanguage"
                class="w-full"
                v-model="student.lang_2"
                :options="gsFilters.languagesList"
                :showClear="true"
                optionLabel="lang_name"
                optionValue="lang_code_str"
              />
              <label for="secondLanguage">{{ $t("secondLanguage") }} </label>
            </span>
            <small
              v-for="error of v$.student.lang_2.$errors"
              :key="error.$uid"
              class="p-error"
            >
              {{ error.$message }} <br />
            </small>
          </div>
        </div>
        <h4 class="mt-1 mb-3 mx-3">{{ $t("subjectGrades") }}</h4>
        <div class="form-container">
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputNumber
                id="arabic"
                class="w-full"
                type="text"
                v-model="student.arabic_deg"
                :maxFractionDigits="2"
                @update:modelValue="calculateTotalDegree"
                :min="0"
              />
              <label for="arabic">{{ $t("arabic") }}</label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputNumber
                id="firstLanguageDeg"
                class="w-full"
                type="text"
                v-model="student.lang_1_deg"
                :maxFractionDigits="2"
                @update:modelValue="calculateTotalDegree"
                :min="0"
              />
              <label for="firstLanguageDeg">{{ $t("firstLanguage") }}</label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputNumber
                id="secondLanguageDeg"
                class="w-full"
                type="text"
                v-model="student.lang_2_deg"
                :maxFractionDigits="2"
                @update:modelValue="calculateTotalDegree"
                :min="0"
              />
              <label for="secondLanguageDeg">{{ $t("secondLanguage") }}</label>
            </span>
          </div>
          <div class="field mt-3 mx-2" v-if="scientificMathBranch === true">
            <span class="p-float-label">
              <InputNumber
                id="pureMath"
                class="w-full"
                type="text"
                v-model="student.pure_math_deg"
                :maxFractionDigits="2"
                @update:modelValue="calculateTotalDegree"
                :min="0"
              />
              <label for="pureMath">{{ $t("pureMath") }}</label>
            </span>
          </div>
          <div class="field mt-3 mx-2" v-if="literar === true">
            <span class="p-float-label">
              <InputNumber
                id="history"
                class="w-full"
                type="text"
                v-model="student.history_deg"
                :maxFractionDigits="2"
                @update:modelValue="calculateTotalDegree"
                :min="0"
              />
              <label for="history">{{ $t("history") }}</label>
            </span>
          </div>
          <div class="field mt-3 mx-2" v-if="literar === true">
            <span class="p-float-label">
              <InputNumber
                id="geography"
                class="w-full"
                type="text"
                v-model="student.geography_deg"
                :maxFractionDigits="2"
                @update:modelValue="calculateTotalDegree"
                :min="0"
              />
              <label for="geography">{{ $t("geography") }}</label>
            </span>
          </div>
          <div class="field mt-3 mx-2" v-if="literar === true">
            <span class="p-float-label">
              <InputNumber
                id="philosophy"
                class="w-full"
                type="text"
                v-model="student.philosophy_deg"
                :maxFractionDigits="2"
                @update:modelValue="calculateTotalDegree"
                :min="0"
              />
              <label for="philosophy">{{ $t("philosophy") }}</label>
            </span>
          </div>
          <div class="field mt-3 mx-2" v-if="literar === true">
            <span class="p-float-label">
              <InputNumber
                id="psychology"
                class="w-full"
                type="text"
                v-model="student.psychology_deg"
                :maxFractionDigits="2"
                @update:modelValue="calculateTotalDegree"
                :min="0"
              />
              <label for="psychology">{{ $t("psychology") }}</label>
            </span>
          </div>
          <div
            class="field mt-3 mx-2"
            v-if="
              scientificMathBranch === true || scientificScienceBranch === true
            "
          >
            <span class="p-float-label">
              <InputNumber
                id="chemistry"
                class="w-full"
                type="text"
                v-model="student.chemistry_deg"
                :maxFractionDigits="2"
                @update:modelValue="calculateTotalDegree"
                :min="0"
              />
              <label for="chemistry">{{ $t("chemistry") }}</label>
            </span>
          </div>
          <div class="field mt-3 mx-2" v-if="scientificScienceBranch === true">
            <span class="p-float-label">
              <InputNumber
                id="biology"
                class="w-full"
                type="text"
                v-model="student.biology_deg"
                :maxFractionDigits="2"
                @update:modelValue="calculateTotalDegree"
                :min="0"
              />
              <label for="biology">{{ $t("biology") }}</label>
            </span>
          </div>
          <div class="field mt-3 mx-2" v-if="scientificScienceBranch === true">
            <span class="p-float-label">
              <InputNumber
                id="geology"
                class="w-full"
                type="text"
                v-model="student.geology_deg"
                :maxFractionDigits="2"
                @update:modelValue="calculateTotalDegree"
                :min="0"
              />
              <label for="geology">{{ $t("geology") }}</label>
            </span>
          </div>
          <div class="field mt-3 mx-2" v-if="scientificMathBranch === true">
            <span class="p-float-label">
              <InputNumber
                id="appliedMath"
                class="w-full"
                type="text"
                v-model="student.applied_math_deg"
                :maxFractionDigits="2"
                @update:modelValue="calculateTotalDegree"
                :min="0"
              />
              <label for="appliedMath">{{ $t("appliedMath") }}</label>
            </span>
          </div>
          <div
            class="field mt-3 mx-2"
            v-if="
              scientificMathBranch === true || scientificScienceBranch === true
            "
          >
            <span class="p-float-label">
              <InputNumber
                id="physics"
                class="w-full"
                type="text"
                v-model="student.physics_deg"
                :maxFractionDigits="2"
                @update:modelValue="calculateTotalDegree"
                :min="0"
              />
              <label for="physics">{{ $t("physics") }}</label>
            </span>
          </div>
          <div class="field mt-3 mx-2" v-if="computedTotalDegree !== -1">
            <span class="p-float-label">
              <InputNumber
                id="totalGradeComputed"
                class="w-full"
                type="text"
                v-model="computedTotalDegree"
                :disabled="true"
              />
              <label for="totalGrade">{{ $t("totalGrade") }}</label>
            </span>
          </div>
          <div class="field mt-3 mx-2" v-else>
            <span class="p-float-label">
              <InputNumber
                id="totalGrade"
                class="w-full"
                type="text"
                v-model="student.total_degree"
                :maxFractionDigits="2"
                :min="0"
              />
              <label for="totalGrade">{{ $t("totalGrade") }}</label>
            </span>
            <small
              v-for="error of v$.student.total_degree.$errors"
              :key="error.$uid"
              class="p-error"
            >
              {{ error.$message }} <br />
            </small>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputNumber
                id="religiousEducation"
                class="w-full"
                type="text"
                v-model="student.religious_education_deg"
                :maxFractionDigits="2"
                :min="0"
              />
              <label for="religiousEducation">{{
                $t("religiousEducation")
              }}</label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputNumber
                id="nationalEducation"
                class="w-full"
                type="text"
                v-model="student.national_education_deg"
                :maxFractionDigits="2"
                :min="0"
              />
              <label for="nationalEducation">{{
                $t("nationalEducation")
              }}</label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputNumber
                id="economics"
                class="w-full"
                type="text"
                v-model="student.economics_deg"
                :maxFractionDigits="2"
                :min="0"
              />
              <label for="economics">{{ $t("economics") }}</label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <InputNumber
                id="noOfFail"
                class="w-full"
                type="text"
                v-model="student.no_of_fail"
                :min="0"
              />
              <label for="noOfFail">{{ $t("noOfFail") }}</label>
            </span>
          </div>
        </div>
      </div>
      <div
        class="header grid justify-content-end p-2 md:flex-row flex-column-reverse"
      >
        <div class="flex md:mt-2 align-items-center">
          <i
            v-if="v$.$invalid && v$.$dirty"
            v-tooltip.bottom="{
              value: $t('invalidFields'),
              class: 'error-tooltip',
            }"
            class="pi pi-exclamation-triangle error-icon text-4xl"
          ></i>
          <Button
            :label="$t('save')"
            type="submit"
            class="save-button p-button p-button-primary p-button-sm flex-grow-1 mx-2 my-auto"
          />
          <Button
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
import InputText from "primevue/inputtext";
import InputNumber from "primevue/inputnumber";
import Dropdown from "primevue/dropdown";
import PageLoader from "../shared/basic/PageLoader.vue";
import { onMounted, ref, type Ref } from "vue";
import {
  createI18nMessage,
  helpers,
  maxLength,
  minLength,
  required,
  type MessageProps,
} from "@vuelidate/validators";
import useVuelidate from "@vuelidate/core";
import { useI18n } from "vue-i18n";
import { InquireCDStudentProvider } from "@/providers/inquireCDStudent";
import {
  Float3DigitPattern,
  IntegerPattern,
  NIDPattern,
  NoSymbolsPattern,
} from "@/utils/enums";
import type { CDStudent, GSFilters } from "@/utils/types";
import { showErrorToastMessage, showToastMessage } from "@/utils/globals";

// Importing Services
const { t } = useI18n();

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// GS Filters
const gsFilters: Ref<GSFilters> = ref({});
const filteredGSFilters: Ref<GSFilters> = ref({});

// Student Data
const student: Ref<CDStudent> = ref({});
const scientificMathBranch: Ref<boolean> = ref(false);
const scientificScienceBranch: Ref<boolean> = ref(false);
const literar: Ref<boolean> = ref(false);
const computedTotalDegree: Ref<number> = ref(-1);

// Define Component Inputs (Props)
const props = defineProps({
  isEdit: { type: Boolean, default: false },
  selectedYear: { type: String, default: "2021" },
  nationalId: { type: String, default: "" },
  seatNumber: { type: Number, default: 0 },
});

// Define Component Outputs (Emits)
const emit = defineEmits(["cancel", "submit"]);

// on mount functions
onMounted(async () => {
  if (props.isEdit && (props.nationalId || props.seatNumber)) {
    await getStudentData(
      props.selectedYear,
      props.nationalId,
      props.seatNumber
    );
    await v$.value.$validate();
  } else {
    await getGSDefaults(props.selectedYear);
    student.value.national_no = props.nationalId;
    setValuesFromNID();
  }
});

// Component Functions
const getGSDefaults = async (selectedYear: string) => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    // Gets GS Defaults
    const result = await InquireCDStudentProvider.gsFilters(selectedYear);
    gsFilters.value = result.payload;
    createFiltersStringAttributes();
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const createFiltersStringAttributes = () => {
  gsFilters.value.studentsBranchList = gsFilters.value.studentsBranchList?.map(
    (branch) => {
      return {
        ...branch,
        branch_code_str: branch.branch_code.toString(),
      };
    }
  );
  gsFilters.value.languagesList = gsFilters.value.languagesList?.map(
    (language) => {
      return {
        ...language,
        lang_code_str: language.lang_code.toString(),
      };
    }
  );
};

const filterAdminstrations = async (clearStudentField = false) => {
  const governorate = gsFilters.value.governorates?.find(
    (governorate) => governorate.governorate_code === student.value.moderia
  );
  const filteredAdmins = gsFilters.value.educationalAdministrations?.filter(
    (admin) => admin.governorate_code === governorate?.governorate_code
  );
  filteredGSFilters.value.educationalAdministrations = filteredAdmins;
  if (clearStudentField) {
    student.value.dept_code = undefined;
  }
};

//sit data based on NID
const setValuesFromNID = () => {
  const is_valid = !v$.value.student.national_no.$invalid;
  if (is_valid) {
    if (student.value.national_no?.substr(0, 1) === "2") {
      student.value.year =
        1900 + Number(student.value.national_no?.substr(1, 2));
    } else {
      student.value.year =
        2000 + Number(student.value.national_no?.substr(1, 2));
    }
    if (student.value.national_no?.substr(3, 1) === "0") {
      student.value.month = Number(student.value.national_no?.substr(4, 1));
    } else {
      student.value.month = Number(student.value.national_no?.substr(3, 2));
    }
    if (student.value.national_no?.substr(5, 1) === "0") {
      student.value.day = Number(student.value.national_no?.substr(6, 1));
    } else {
      student.value.day = Number(student.value.national_no?.substr(5, 2));
    }
    student.value.date_of_birth =
      student.value.day + "-" + student.value.month + "-" + student.value.year;

    if (Number(student.value.national_no?.substr(12, 1)) % 2 === 0) {
      student.value.gender_id = 2;
    } else {
      student.value.gender_id = 1;
    }
    student.value.birth_palace = gsFilters.value.governorates?.find(
      (element) => {
        if (student.value.national_no?.substr(7, 1) === "0") {
          return (
            element.governorate_code ===
            Number(student.value.national_no?.substr(8, 1))
          );
        } else {
          return (
            element.governorate_code ===
            Number(student.value.national_no?.substr(7, 2))
          );
        }
      }
    )?.governorate_name;
  }
};

const setStudentBranchFlags = () => {
  // Set Branch
  scientificMathBranch.value = false;
  scientificScienceBranch.value = false;
  literar.value = false;
  if (student.value.branch_code_new === 1) {
    scientificScienceBranch.value = true;
  } else if (student.value.branch_code_new === 2) {
    scientificMathBranch.value = true;
  } else if (student.value.branch_code_new === 5) {
    literar.value = true;
  } else {
    scientificMathBranch.value = true;
    scientificScienceBranch.value = true;
    literar.value = true;
  }
};

const calculateTotalDegree = () => {
  let total = 0;
  let uncalculatedDegrees = 0;
  let degrees = [
    student.value.arabic_deg,
    student.value.lang_1_deg,
    student.value.lang_2_deg,
    student.value.pure_math_deg,
    student.value.history_deg,
    student.value.geography_deg,
    student.value.philosophy_deg,
    student.value.psychology_deg,
    student.value.chemistry_deg,
    student.value.biology_deg,
    student.value.geology_deg,
    student.value.applied_math_deg,
    student.value.physics_deg,
  ];
  for (const degree of degrees) {
    if (degree && degree >= 0) {
      total += degree;
    } else {
      uncalculatedDegrees += 1;
    }
  }
  if (uncalculatedDegrees === degrees.length) {
    computedTotalDegree.value = -1;
    return -1;
  }
  computedTotalDegree.value = total;
  student.value.total_degree = total;
  return total;
};

// Component Functions
const cancel = () => {
  emit("cancel");
};

// Provider related Functions
const getStudentData = async (
  selectedYear: string,
  nationalId: string,
  seatNumber: number
) => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const result = await InquireCDStudentProvider.getStudent(
      selectedYear,
      nationalId,
      seatNumber
    );
    await getGSDefaults(props.selectedYear);
    student.value = result.payload.student;
    student.value.school_code = student.value.school_code?.toString();
    student.value.branch_code_new = student.value.branch_code_new?.toString();
    student.value.lang_1 = student.value.lang_1?.toString();
    student.value.lang_2 = student.value.lang_2?.toString();
    student.value.date_of_birth =
      student.value.day + "-" + student.value.month + "-" + student.value.year;
    // Sets absolute values for extra degrees
    student.value.religious_education_deg = student.value
      .religious_education_deg
      ? Math.abs(student.value.religious_education_deg)
      : undefined;
    student.value.national_education_deg = student.value.national_education_deg
      ? Math.abs(student.value.national_education_deg)
      : undefined;
    student.value.economics_deg = student.value.economics_deg
      ? Math.abs(student.value.economics_deg)
      : undefined;
    setStudentBranchFlags();
    filterAdminstrations();
    calculateTotalDegree();
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const submitStudentForm = async () => {
  if (computedTotalDegree.value !== -1) {
    student.value.total_degree = computedTotalDegree.value;
  }
  const governorate = gsFilters.value.governorates?.find(
    (governorate) => governorate.governorate_code === student.value.moderia
  );
  student.value.city_name = governorate?.governorate_name;
  const adminstration = gsFilters.value.educationalAdministrations?.find(
    (adminstration) => adminstration.edu_admin_code === student.value.dept_code
  );
  student.value.dept_name = adminstration?.edu_admin_name;
  if (!props.isEdit) {
    student.value.national_no = props.nationalId;
  }
  const isValid = await v$.value.$validate();
  isLoading.value = true;
  if (isValid) {
    try {
      if (props.isEdit) {
        const result = await InquireCDStudentProvider.editStudent(
          props.selectedYear,
          props.nationalId,
          props.seatNumber,
          student.value
        );
        showToastMessage(result.detail);
      } else {
        const result = await InquireCDStudentProvider.addStudent(
          props.selectedYear,
          student.value
        );
        showToastMessage(result.detail);
      }
      emit("submit", student.value);
    } catch (error) {
      showErrorToastMessage(error);
    }
  }
  isLoading.value = false;
};

// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `addEditStudentValidations.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

// Custom Validators
const checkIntNumberType = helpers.regex(IntegerPattern);
const checkFloatNumberType = helpers.regex(Float3DigitPattern);
const checkNIDNumber = helpers.regex(NIDPattern);
const checkStudentNameText = helpers.regex(NoSymbolsPattern);

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
    return filteredLengths.length > 3;
  }
  return true;
};

const checkLanguagesValues = () => {
  if (!student.value.lang_1 || !student.value.lang_2) {
    return true;
  }
  if (student.value.lang_2 === 6 || student.value.lang_2 === 0) {
    return true;
  } else {
    return !(student.value.lang_2 === student.value.lang_1);
  }
};

// Validation Rules
const rules = {
  student: {
    arabic_name: {
      checkName: withI18nMessage(required),
      requiredStudentEachNameLength: withI18nMessage(checkEachNameLength),
      requiredStudentNameLength: withI18nMessage(checkNameLength),
      textFieldMaxLength: withI18nMessage(maxLength(100)),
      checkStudentNameText: withI18nMessage(checkStudentNameText),
    },
    national_no: {
      checkNID: withI18nMessage(required),
      checkNIDNumberLength: withI18nMessage(minLength(14)),
      checkNIDNumber: withI18nMessage(checkNIDNumber),
    },
    seating_no: {
      checkSeatNumber: withI18nMessage(required),
      checkIntegerNumberType: withI18nMessage(checkIntNumberType),
      fieldMaxLength: withI18nMessage(maxLength(9)),
    },
    school_name: {
      textFieldMaxLength: withI18nMessage(maxLength(100)),
    },
    birth_palace: {
      textFieldMaxLength: withI18nMessage(maxLength(200)),
    },
    branch_code_new: {
      checkStudentBranch: withI18nMessage(required),
    },
    tanseq_number: {
      fieldMaxLength: withI18nMessage(maxLength(9)),
      checkTansiqNumber: withI18nMessage(required),
      checkIntegerNumberType: withI18nMessage(checkIntNumberType),
    },
    total_degree: {
      checkTotalGrades: withI18nMessage(required),
      checkNumberType: withI18nMessage(checkFloatNumberType),
    },
    lang_2: {
      checkLanguages: withI18nMessage(checkLanguagesValues),
    },
    bar_code: {
      alphanumericFieldMaxLength: withI18nMessage(maxLength(75)),
    },
    address: {
      textFieldMaxLength: withI18nMessage(maxLength(250)),
    },
    police_station: {
      textFieldMaxLength: withI18nMessage(maxLength(100)),
    },
  },
};

// Set up component Validation
const v$ = useVuelidate(rules, { student });
</script>

<style scoped lang="scss">
.form-container {
  display: grid;
  grid-template-columns: 1fr;
}
@media screen and (min-width: 768px) {
  .form-container {
    grid-template-columns: 1fr 1fr;
  }
}
@media screen and (min-width: 992px) {
  .form-container {
    grid-template-columns: 1fr 1fr 1fr;
  }
}
.save-button {
  min-width: 6rem;
}
</style>
