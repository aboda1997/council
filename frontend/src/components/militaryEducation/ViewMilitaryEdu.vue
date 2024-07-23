<template>
  <PageLoader
    v-if="isLoading || errorMessage"
    :loading="isLoading"
    :error="errorMessage"
  />
  <template v-else>
    <div class="flex flex-column w-full">
      <div
        class="header grid justify-content-between px-2 pt-2 md:flex-row flex-column-reverse"
      >
        <SignatureValue :signature="signature" />
        <div class="button-wrapper flex md:mt-2">
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
      <StudentMilitaryEduDetails :studentMilitaryEduData="studentMilitaryEdu" />
    </div>
  </template>
</template>

<script setup lang="ts">
import Button from "primevue/button";
import SignatureValue from "../shared/basic/SignatureValue.vue";
import PageLoader from "../shared/basic/PageLoader.vue";
import StudentMilitaryEduDetails from "../shared/studentDetails/StudentMilitaryEduDetails.vue";
import { onMounted, ref, type Ref } from "vue";
import { ApplicationEnum, RightsEnum } from "@/utils/enums";
import type { Signature, StudentMilitaryEdu } from "@/utils/types";
import { MilitaryEducationProvider } from "@/providers/militaryEducation";

// Static Variables
const app = ApplicationEnum.MILITARY_EDUCATION;

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// Student Data
const studentMilitaryEdu: Ref<StudentMilitaryEdu> = ref({});
const signature: Ref<Signature | undefined> = ref();

// Define Component Inputs (Props)
const props = defineProps({
  studentId: { type: Number, default: 13 },
});

// Define Component Outputs (Emits)
const emit = defineEmits(["edit", "delete", "notFound"]);

onMounted(async () => {
  if (props.studentId) {
    await getStudentData(props.studentId);
  }
});

const getStudentData = async (studentId: number) => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const result = await MilitaryEducationProvider.getStudentData(studentId);
    studentMilitaryEdu.value = result.payload.studentMilitaryEdu;
    signature.value = result.payload.signature;
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const editStudent = () => {
  emit("edit", studentMilitaryEdu.value);
};

const deleteStudent = () => {
  emit("delete", studentMilitaryEdu.value);
};
</script>

<style scoped></style>
