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
        <div class="button-wrapper flex md:mt-2">
          <Button
            :label="$t('studentHistory')"
            icon="pi pi-history icon-fix"
            class="p-button p-button-secondary p-button-sm flex-grow-1 mx-2 my-auto"
            @click="viewStudentHistory()"
          />
          <Button
            v-if="$hasPermission(app, RightsEnum.EDIT)"
            :label="$t('edit')"
            icon="pi pi-pencil"
            class="p-button p-button-warning p-button-sm flex-grow-1 mx-2 my-auto"
            @click="editStudent()"
          />
          <Button
            v-if="$hasPermission(app, RightsEnum.DELETE)"
            :label="$t('delete')"
            icon="pi pi-trash"
            class="p-button p-button-danger p-button-sm flex-grow-1 mx-2 my-auto"
            @click="deleteStudent()"
          />
        </div>
      </div>
      <StudentBasicDetails :studentData="student" />
      <StudentSecondaryDetails
        v-if="studentSecondaryEdu"
        :studentSecondaryEduData="studentSecondaryEdu"
        :studentStatusId="student.studentStatus_id"
      />
      <StudentUniversityDetails
        v-if="studentUniversityEdu"
        :showGraduationData="hasGraduated"
        :studentUniversityEduData="studentUniversityEdu"
        :studentImposedCoursesData="studentImposedCourses"
      />
      <StudentTransferDetails
        v-if="hasTransferred"
        :studentUniversityEduData="studentUniversityEdu"
      />
      <StudentMilitaryEduDetails
        :studentMilitaryEduData="studentMilitaryEdu"
        :studentGenderIdstudentGenderId="student.studentGender_id"
        :studentNationalityId="student.studentNationality_id"
      />
      <div>
        <h4 class="mt-2 mb-2 mx-2">
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
    </div>
  </template>
</template>

<script setup lang="ts">
import Button from "primevue/button";
import PageLoader from "../shared/basic/PageLoader.vue";
import SignatureValue from "../shared/basic/SignatureValue.vue";
import StudentBasicDetails from "../shared/studentDetails/StudentBasicDetails.vue";
import StudentSecondaryDetails from "../shared/studentDetails/StudentSecondaryDetails.vue";
import StudentUniversityDetails from "../shared/studentDetails/StudentUniversityDetails.vue";
import StudentMilitaryEduDetails from "../shared/studentDetails/StudentMilitaryEduDetails.vue";
import StudentTransferDetails from "../shared/studentDetails/studentTransferDetails.vue";
import StudentFileUpload from "../shared/fileUpload/StudentFileUpload.vue";
import { computed, onMounted, ref, type Ref } from "vue";
import {
  ApplicationEnum,
  RegistrationTypeEnum,
  RightsEnum,
  StudentStatus,
} from "@/utils/enums";
import type {
  Student,
  StudentImposedCourse,
  StudentSecondaryEdu,
  StudentUniversityEdu,
  Signature,
  StudentMilitaryEdu,
  UploadedFile,
} from "@/utils/types";
import { InquireStudentInfoProvider } from "@/providers/inquireStudentInfo";

// Static Variables
const app = ApplicationEnum.STUDENT_INFO;

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// Student Data
const student: Ref<Student> = ref({});
const studentSecondaryEdu: Ref<StudentSecondaryEdu | undefined> = ref();
const studentUniversityEdu: Ref<StudentUniversityEdu | undefined> = ref();
const studentImposedCourses: Ref<StudentImposedCourse[] | undefined> = ref();
const studentMilitaryEdu: Ref<StudentMilitaryEdu> = ref({});
const studentAttachment: Ref<UploadedFile[] | undefined> = ref();
const signature: Ref<Signature | undefined> = ref();

// Computed Values
const hasGraduated = computed(() => {
  return student.value.studentStatus_id === StudentStatus.GRADUATE;
});

const hasTransferred = computed(() => {
  return (
    studentUniversityEdu.value &&
    (studentUniversityEdu.value.transferDate ||
      studentUniversityEdu.value.studentRegistrationType_id ==
        RegistrationTypeEnum.TRANSFER)
  );
});

// Define Component Inputs (Props)
const props = defineProps({
  studentId: { type: Number, default: -1 },
});

// Define Component Outputs (Emits)
const emit = defineEmits(["history", "edit", "delete"]);

onMounted(async () => {
  if (props.studentId) {
    await getStudentData(props.studentId);
  }
});

const getStudentData = async (studentId: number) => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const result = await InquireStudentInfoProvider.getStudent(studentId);
    student.value = result.payload.student;
    studentSecondaryEdu.value = result.payload.studentSecondaryEdu;
    studentUniversityEdu.value = result.payload.studentUniversityEdu;
    studentImposedCourses.value = result.payload.studentImposedCourses;
    studentMilitaryEdu.value = result.payload.studentMilitaryEdu;
    studentAttachment.value = result.payload.attachments;
    signature.value = result.payload.signature;
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const viewStudentHistory = () => {
  emit("history", student.value);
};

const editStudent = () => {
  emit("edit", student.value);
};

const deleteStudent = () => {
  emit("delete", student.value);
};
</script>

<style scoped></style>
