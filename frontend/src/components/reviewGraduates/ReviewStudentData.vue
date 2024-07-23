<template>
  <PageLoader
    v-if="isLoading || errorMessage"
    :loading="isLoading"
    :error="errorMessage"
  />
  <template v-else>
    <div class="flex flex-column">
      <div
        class="header grid justify-content-between px-2 pt-2 md:flex-row flex-column-reverse"
      >
        <SignatureValue :signature="signature" />
      </div>
      <StudentBasicDetails :studentData="student" />
      <StudentSecondaryDetails
        v-if="studentSecondaryEdu"
        :studentSecondaryEduData="studentSecondaryEdu"
        :studentStatusId="student.studentStatus_id"
      />
      <StudentUniversityDetails
        v-if="studentUniversityEdu"
        :showGraduationData="!showReviewForm"
        :studentUniversityEduData="studentUniversityEdu"
        :studentImposedCoursesData="studentImposedCourses"
      />
      <StudentGraduationDetails
        v-if="!showReviewForm"
        :studentUniversityEduData="studentUniversityEdu"
      />
      <StudentMilitaryEduDetails
        :studentMilitaryEduData="studentMilitaryEdu"
        :studentGenderId="student.studentGender_id"
        :studentNationalityId="student.studentNationality_id"
      />
      <form
        v-if="showReviewForm"
        @submit.prevent="confirmSubmitForm"
        form="ReviewGraduationDataForm"
      >
        <h4 class="mt-2 mb-3 mx-2">
          {{ $t("graduationData") }}
        </h4>
        <StudentGraduationForm
          :formFilters="formFilters"
          v-model:studentUniversityEdu="studentUniversityEdu"
          @submit="editStudentData"
        />
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
          </div>
        </div>
      </form>
    </div>
  </template>
</template>

<script setup lang="ts">
import Button from "primevue/button";
import PageLoader from "../shared/basic/PageLoader.vue";
import SignatureValue from "../shared/basic/SignatureValue.vue";
import StudentGraduationForm from "../shared/studentForms/StudentGraduationForm.vue";
import StudentBasicDetails from "../shared/studentDetails/StudentBasicDetails.vue";
import StudentSecondaryDetails from "../shared/studentDetails/StudentSecondaryDetails.vue";
import StudentUniversityDetails from "../shared/studentDetails/StudentUniversityDetails.vue";
import StudentGraduationDetails from "../shared/studentDetails/StudentGraduationDetails.vue";
import StudentMilitaryEduDetails from "../shared/studentDetails/StudentMilitaryEduDetails.vue";
import { onMounted, ref, type Ref } from "vue";
import type {
  CouncilFilters,
  Student,
  StudentImposedCourse,
  StudentSecondaryEdu,
  StudentUniversityEdu,
  Signature,
  StudentMilitaryEdu,
} from "@/utils/types";
import { ReviewGraduatesProvider } from "@/providers/reviewGraduates";
import {
  showConfirmDialog,
  showErrorToastMessage,
  showToastMessage,
} from "@/utils/globals";
import { ConfirmDialogTypes, StudentStatus } from "@/utils/enums";
import useVuelidate from "@vuelidate/core";
import { useI18n } from "vue-i18n";

// Services
const { t } = useI18n();

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// Student Data
const student: Ref<Student> = ref({});
const studentSecondaryEdu: Ref<StudentSecondaryEdu | undefined> = ref();
const studentUniversityEdu: Ref<StudentUniversityEdu | undefined> = ref();
const studentImposedCourses: Ref<StudentImposedCourse[] | undefined> = ref();
const studentMilitaryEdu: Ref<StudentMilitaryEdu> = ref({});
const signature: Ref<Signature | undefined> = ref();
const formFilters: Ref<CouncilFilters> = ref({});

// Define Component Inputs (Props)
const props = defineProps({
  studentId: { type: Number, default: 0 },
  selectedStudentType: { type: String },
  showReviewForm: { type: Boolean, default: false },
});

onMounted(async () => {
  if (props.studentId) {
    await getStudentData(props.studentId, props.selectedStudentType);
  }
  if (props.showReviewForm) {
    await getDefaults();
  }
});

// Define Component Outputs (Emits)
const emit = defineEmits(["statusUpdated"]);

// Component Functions
const confirmSubmitForm = async () => {
  const isValid = await v$.value.$validate();
  if (isValid) {
    showConfirmDialog(
      t("reviewConfirmMessage"),
      submitStudentForm,
      ConfirmDialogTypes.CONFIRM
    );
  }
};

const submitStudentForm = async (confirm: boolean) => {
  if (confirm) {
    await editStudentData(studentUniversityEdu.value);
  }
};

// Provider Functions
const getDefaults = async () => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    // Gets GS Defaults
    const result = await ReviewGraduatesProvider.formFilters();
    formFilters.value = result.payload;
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const getStudentData = async (
  studentId: number,
  selectedStudentType?: string
) => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const result = await ReviewGraduatesProvider.getStudent(
      studentId,
      selectedStudentType
    );
    student.value = result.payload.student;
    studentSecondaryEdu.value = result.payload.studentSecondaryEdu;
    studentUniversityEdu.value = result.payload.studentUniversityEdu;
    studentImposedCourses.value = result.payload.studentImposedCourses;
    studentMilitaryEdu.value = result.payload.studentMilitaryEdu;
    signature.value = result.payload.signature;
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const editStudentData = async (
  studentUniversityEdu: StudentUniversityEdu | undefined
) => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    if (studentUniversityEdu) {
      const result = await ReviewGraduatesProvider.editStudentData(
        props.studentId,
        studentUniversityEdu
      );
      emit("statusUpdated", {
        id: StudentStatus.GRADUATE,
        name:
          formFilters.value.status?.find(
            (status) => status.id === StudentStatus.GRADUATE
          )?.name || "",
      });
      showToastMessage(result.detail);
    }
  } catch (error) {
    showErrorToastMessage(error);
  }
  isLoading.value = false;
};

const v$ = useVuelidate();
</script>

<style scoped lang="scss">
.save-button {
  min-width: 6rem;
}
</style>
