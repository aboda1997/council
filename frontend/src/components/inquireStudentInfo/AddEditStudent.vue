<template>
  <PageLoader
    v-if="isLoading || errorMessage"
    :loading="isLoading"
    :error="errorMessage"
  />
  <template v-else>
    <form @submit.prevent="submit" form="AddEditCDStudentForm">
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
      </div>
      <StudentBasicForm
        :isEdit="props.isEdit"
        :formFilters="formFilters"
        :studentOriginalNID="studentOriginalData?.student?.studentNID"
        :studentOriginalStatus="studentOriginalData?.student?.studentStatus_id"
        :studentRegistrationTypeId="
          studentUniversityEdu.studentRegistrationType_id
        "
        :studentSecondaryCertId="
          studentOriginalData?.studentSecondaryEdu?.studentSecondaryCert_id
        "
        v-bind:student="student"
      />
      <template v-if="studentSecondaryEdu">
        <h4 class="mt-1 mb-3 mx-3">
          {{ $t("secEduData") }}
        </h4>
        <StudentSecondaryForm
          :isEdit="props.isEdit"
          :formFilters="formFilters"
          :studentStatusId="student.studentStatus_id"
          v-bind:studentSecondaryEdu="studentSecondaryEdu"
        />
      </template>
      <template v-if="studentUniversityEdu">
        <h4 class="mt-1 mb-3 mx-3">
          {{ $t("uniEduData") }}
        </h4>
        <StudentUniversityForm
          :isEdit="props.isEdit"
          :formFilters="formFilters"
          :studentStatusId="student.studentStatus_id"
          :studentImposedCourses="studentImposedCourses"
          @update:studentImposedCourses="updateImposedCourses"
          v-bind:studentUniversityEdu="studentUniversityEdu"
        />
      </template>
      <template v-if="hasTransferred">
        <h4 class="mt-1 mb-3 mx-3">
          {{ $t("transferData") }}
        </h4>
        <StudentTransferForm
          :formFilters="formFilters"
          :studentStatusId="student.studentStatus_id"
          v-bind:studentUniversityEdu="studentUniversityEdu"
        />
      </template>
      <template v-if="studentMilitaryEduApplicable">
        <h4 class="mt-1 mb-3 mx-3">
          {{ $t("militaryEduData") }}
        </h4>
        <StudentMilitaryEduForm
          :studentStatusId="student.studentStatus_id"
          v-bind:studentMilitaryEdu="studentMilitaryEdu"
        />
      </template>
      <div>
        <h4 class="mt-1 mb-3 mx-3">
          {{ $t("attachments") }}
        </h4>
        <StudentFileUpload
          :allowDelete="$hasPermission(app, RightsEnum.EDIT)"
          :provider="InquireStudentInfoProvider"
          :studentUniqueId="student.uniqueId"
          :attachments="studentAttachment"
          :maxAttachmentsCount="5"
          :maxAttachmentSize="2097152"
          :allowedMimetype="[
            'image/png',
            'image/jpg',
            'image/jpeg',
            'application/pdf',
          ]"
        />
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
import PageLoader from "../shared/basic/PageLoader.vue";
import StudentBasicForm from "../shared/studentForms/StudentBasicForm.vue";
import StudentSecondaryForm from "../shared/studentForms/StudentSecondaryForm.vue";
import StudentUniversityForm from "../shared/studentForms/StudentUniversityForm.vue";
import StudentMilitaryEduForm from "../shared/studentForms/StudentMilitaryEduForm.vue";
import StudentFileUpload from "../shared/fileUpload/StudentFileUpload.vue";
import { computed, onMounted, ref, type PropType, type Ref } from "vue";
import { useI18n } from "vue-i18n";
import {
  ApplicationEnum,
  CertificateEnum,
  ConfirmDialogTypes,
  CountryEnum,
  GenderEnum,
  RegistrationTypeEnum,
  RightsEnum,
  StudentStatus,
  TotalEquivDegree,
} from "@/utils/enums";
import type {
  CouncilFilters,
  Student,
  StudentMilitaryEdu,
  StudentSecondaryEdu,
  StudentUniversityEdu,
  StudentImposedCourse,
  StudentViewPayload,
  InquireStudentQuery,
  SecondaryGSInfo,
  UploadedFile,
} from "@/utils/types";
import {
  showConfirmDialog,
  showErrorToastMessage,
  showToastMessage,
} from "@/utils/globals";
import { InquireStudentInfoProvider } from "@/providers/inquireStudentInfo";
import useVuelidate from "@vuelidate/core";
import StudentTransferForm from "../shared/studentForms/StudentTransferForm.vue";

// Static Variables
const app = ApplicationEnum.TRANSFER_STUDENTS;

// Importing Services
const { t } = useI18n();

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// Form Filters
const formFilters: Ref<CouncilFilters> = ref({});

// Student Data
const student: Ref<Student> = ref({});
const studentSecondaryEdu: Ref<StudentSecondaryEdu> = ref({});
const studentUniversityEdu: Ref<StudentUniversityEdu> = ref({});
const studentImposedCourses: Ref<StudentImposedCourse[] | undefined> = ref([]);
const studentMilitaryEdu: Ref<StudentMilitaryEdu> = ref({});
const studentAttachment: Ref<UploadedFile[] | undefined> = ref();
const studentOriginalData: Ref<StudentViewPayload | undefined> = ref();

// Computed Student Data
const studentDegreePercentage = computed(() => {
  if (
    studentSecondaryEdu.value &&
    studentSecondaryEdu.value.studentSecondaryCert_id ===
      CertificateEnum.EGYPTIAN_GENERAL_SECONADARY &&
    studentSecondaryEdu.value.studentTot
  ) {
    let sportDegree = studentSecondaryEdu.value.studentSportDegree || 0;
    let complainGainDegree = studentSecondaryEdu.value.studentComplainGain || 0;
    let total =
      +studentSecondaryEdu.value.studentTot +
      +sportDegree +
      +complainGainDegree;
    return Math.round(((total * 100) / TotalEquivDegree) * 100) / 100;
  } else if (studentSecondaryEdu.value?.studentEquivTot) {
    return (
      Math.round(
        ((studentSecondaryEdu.value.studentEquivTot * 100) / TotalEquivDegree) *
          100
      ) / 100
    );
  }
  return undefined;
});

const hasTransferred = computed(() => {
  return (
    studentUniversityEdu.value &&
    (studentUniversityEdu.value.transferDate ||
      studentUniversityEdu.value.studentRegistrationType_id ==
        RegistrationTypeEnum.TRANSFER)
  );
});

const studentMilitaryEduApplicable = computed(() => {
  return (
    props.isEdit &&
    student.value.studentGender_id === GenderEnum.MALE &&
    (!student.value.studentNationality_id ||
      student.value.studentNationality_id === CountryEnum.EGYPT)
  );
});

// Define Component Inputs (Props)
const props = defineProps({
  isEdit: { type: Boolean, default: true },
  studentId: { type: Number, default: 0 },
  secondaryGSInfo: {
    type: Object as PropType<SecondaryGSInfo>,
    default: () => {
      return {};
    },
  },
  searchQuery: {
    type: Object as PropType<InquireStudentQuery>,
    default: () => {
      return {};
    },
  },
});

// Define Component Outputs (Emits)
const emit = defineEmits(["cancel", "submit"]);

// on mount functions
onMounted(async () => {
  if (props.isEdit && props.studentId) {
    await getStudentData(props.studentId);
    await v$.value.$validate();
  } else {
    await getDefaults();
    studentUniversityEdu.value.studentRegistrationType_id =
      RegistrationTypeEnum.PRIMARY;
    if (props.searchQuery && props.searchQuery.nationalID) {
      student.value.studentNID = props.searchQuery.nationalID
        ? Number(props.searchQuery.nationalID)
        : undefined;
      student.value.studentNationality_id = CountryEnum.EGYPT;
    }
    if (props.secondaryGSInfo) {
      student.value = { ...student.value, ...props.secondaryGSInfo.student };
      studentSecondaryEdu.value = {
        ...studentSecondaryEdu.value,
        ...props.secondaryGSInfo.studentSecondaryEdu,
      };
    }
  }
});

// Component Functions
const updateImposedCourses = (value: StudentImposedCourse[]) => {
  studentImposedCourses.value = value;
};

const submit = async () => {
  const isValid = await v$.value.$validate();
  if (isValid) {
    if (!props.isEdit) {
      showConfirmDialog(
        t("addStudentConfirmMessage"),
        (confirm: boolean) => {
          if (confirm) {
            submitStudentForm();
          }
        },
        ConfirmDialogTypes.CONFIRM
      );
    } else if (
      student.value.studentStatus_id == StudentStatus.WITHDRAWN &&
      student.value.studentStatus_id !=
        studentOriginalData.value?.student.studentStatus_id
    ) {
      showConfirmDialog(
        t("statusWithdrawChangeConfirmMessage"),
        (confirm: boolean) => {
          if (confirm) {
            submitStudentForm();
          }
        },
        ConfirmDialogTypes.CONFIRM
      );
    } else if (
      studentOriginalData.value?.student.studentStatus_id ==
        StudentStatus.INITIALLY_ACCEPTED &&
      student.value.studentStatus_id !=
        studentOriginalData.value?.student.studentStatus_id
    ) {
      showConfirmDialog(
        t("statusChangeConfirmMessage"),
        (confirm: boolean) => {
          if (confirm) {
            submitStudentForm();
          }
        },
        ConfirmDialogTypes.CONFIRM
      );
    } else {
      submitStudentForm();
    }
  }
};

const cancel = () => {
  emit("cancel");
};

// Provider related Functions
const getDefaults = async () => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    // Gets GS Defaults
    const result = await InquireStudentInfoProvider.formFilters();
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
    const result = await InquireStudentInfoProvider.getStudent(Id);
    student.value = result.payload.student;
    studentSecondaryEdu.value = result.payload.studentSecondaryEdu;
    studentUniversityEdu.value = result.payload.studentUniversityEdu;
    studentImposedCourses.value = result.payload.studentImposedCourses.map(
      (imposedCourse) => {
        return {
          imposedCourse_id: imposedCourse.imposedCourse_id,
          completed: imposedCourse.completed,
        };
      }
    );
    studentMilitaryEdu.value = result.payload.studentMilitaryEdu;
    studentAttachment.value = result.payload.attachments;
    studentOriginalData.value = JSON.parse(JSON.stringify(result.payload));
    await getDefaults();
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const submitStudentForm = async () => {
  isLoading.value = true;
  try {
    if (props.isEdit) {
      const result = await InquireStudentInfoProvider.editStudent(
        props.studentId,
        student.value,
        studentSecondaryEdu.value,
        studentUniversityEdu.value,
        studentImposedCourses.value
      );
      showToastMessage(result.detail);
    } else {
      const result = await InquireStudentInfoProvider.addStudent(
        student.value,
        studentSecondaryEdu.value,
        studentUniversityEdu.value,
        studentImposedCourses.value
      );
      showToastMessage(result.detail);
    }
    student.value.studentNationality__name = formFilters.value.countries?.find(
      (country) => country.id === student.value.studentNationality_id
    )?.name;
    student.value.studentStatus__name = formFilters.value.status?.find(
      (status) => status.id === student.value.studentStatus_id
    )?.name;
    studentSecondaryEdu.value.studentSecondaryCert__name =
      formFilters.value.certificates?.find(
        (certificate) =>
          certificate.id === studentSecondaryEdu.value.studentSecondaryCert_id
      )?.name;
    studentSecondaryEdu.value.studentCertificateYear__name =
      formFilters.value.years?.find(
        (year) =>
          year.id === studentSecondaryEdu.value.studentCertificateYear_id
      )?.name;
    emit("submit", {
      student: student.value,
      studentSecondaryEdu: studentSecondaryEdu.value,
      studentUniversityEdu: studentUniversityEdu.value,
      studentDegreePercentage: studentDegreePercentage.value,
    });
  } catch (error) {
    showErrorToastMessage(error);
  }
  isLoading.value = false;
};

const v$ = useVuelidate();
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
