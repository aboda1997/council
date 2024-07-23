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
        <h3 class="mt-3 mb-2 mx-2">
          <span>
            {{ $t("studentHistory") }}
          </span>
          <span v-if="student && student.studentName">
            {{ "&nbsp;" + $serverTranslate(student.studentName) }}</span
          >
        </h3>
        <div class="button-wrapper flex md:mt-2">
          <Button
            :label="$t('studentData')"
            icon="pi pi-list icon-fix"
            class="p-button p-button-secondary p-button-sm flex-grow-1 mx-2 my-auto"
            @click="viewStudent()"
          />
        </div>
      </div>
      <StudentHistoryTimeline
        v-if="transactions"
        :showTransferButton="$hasPermission(app, RightsEnum.EDIT)"
        :transactions="transactions"
        @revert="confirmTransaction"
      />
    </div>
  </template>
</template>

<script setup lang="ts">
import Button from "primevue/button";
import PageLoader from "../shared/basic/PageLoader.vue";
import StudentHistoryTimeline from "../shared/studentDetails/StudentHistoryTimeline.vue";
import { useI18n } from "vue-i18n";
import { onMounted, ref, type Ref } from "vue";
import { InquireStudentInfoProvider } from "@/providers/inquireStudentInfo";
import type { Student, StudentTransaction } from "@/utils/types";
import { ApplicationEnum, ConfirmDialogTypes, RightsEnum } from "@/utils/enums";
import {
  showConfirmDialog,
  showErrorToastMessage,
  showToastMessage,
} from "@/utils/globals";

// Imports Services
const { t } = useI18n();

// Static Variables
const app = ApplicationEnum.STUDENT_INFO;

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// Student Data
const student: Ref<Student> = ref({});
const transactions: Ref<StudentTransaction[]> = ref([]);

// Define Component Inputs (Props)
const props = defineProps({
  studentId: { type: Number, default: -1 },
});

// Define Component Outputs (Emits)
const emit = defineEmits(["view"]);

onMounted(async () => {
  if (props.studentId) {
    await getStudentHistory(props.studentId);
  }
});

const confirmTransaction = async (transactionId: number) => {
  showConfirmDialog(
    t("revertEditConfirmMessage"),
    (confirm: boolean) => {
      if (confirm) {
        revertTransaction(props.studentId, transactionId);
      }
    },
    ConfirmDialogTypes.CONFIRM
  );
};

const revertTransaction = async (studentId: number, transactionId: number) => {
  isLoading.value = true;
  try {
    const result = await InquireStudentInfoProvider.revertTransaction(
      studentId,
      transactionId
    );
    showToastMessage(result.detail);
    emit("view", result.payload);
  } catch (error) {
    showErrorToastMessage(error);
  }
  isLoading.value = false;
};

const getStudentHistory = async (studentId: number) => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const result = await InquireStudentInfoProvider.getStudentHistory(
      studentId
    );
    student.value = result.payload.student;
    transactions.value = result.payload.transactions;
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const viewStudent = () => {
  emit("view");
};
</script>

<style lang="scss" scoped>
.labeled-value {
  background: hsl(282, 84%, 97%);
  border-width: 0px;
  border-inline-start: 2px solid var(--primary-color);
  background-color: var(--surface-50);
  border-radius: 0.35rem;
  text-align: start;
  margin-block-end: 0.5rem;
  padding: 0.5rem;
  p {
    margin: 0px;
    line-height: 1.25rem;
    font-size: 0.9rem;
  }
  .label {
    font-weight: normal;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }
  .value {
    font-weight: bold;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }
  .signature {
    font-size: 0.75rem;
  }
}
.custom-marker {
  display: flex;
  width: 2rem;
  height: 2rem;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  border-radius: 50%;
  z-index: 1;
  background: var(--primary-color);
}

::v-deep(.p-timeline-event-content),
::v-deep(.p-timeline-event-opposite) {
  line-height: 1;
}

::v-deep(.p-timeline-event-opposite) {
  flex: 0;
}

@media screen and (max-width: 960px) {
  ::v-deep(.customized-timeline) {
    .p-timeline-event:nth-child(even) {
      flex-direction: row !important;
    }
  }
}
</style>
