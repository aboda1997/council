<template>
  <div class="p-app-container">
    <div class="p-card p-app-card flex flex-column">
      <StudentFilters @search="getStudentsList" @clear="clearStudentsList" />
      <div class="p-seperator"></div>
      <ExpandableTable
        v-if="!showAddForm"
        :is-loading="isLoading"
        :error-message="errorMessage"
        :columns="tableColumns"
        :records="students"
        :total-records="totalRecords"
        v-bind:searchQuery="searchQuery"
        @query-change="getStudentsList(searchQuery, false)"
      >
        <template #expansion="slotProps">
          <div class="flex flex-column">
            <AddEditStudent
              v-if="expandedEditRows.indexOf(slotProps.data) !== -1"
              :is-edit="true"
              :studentId="slotProps.data.id"
              @cancel="switchToViewStudent(slotProps.data)"
              @submit="switchToViewStudent(slotProps.data, $event)"
            />
            <ViewStudentHistory
              v-else-if="expandedHistoryRows.indexOf(slotProps.data) !== -1"
              :studentId="slotProps.data.id"
              @view="switchToViewStudent(slotProps.data, $event)"
            />
            <ViewStudent
              v-else
              :studentId="slotProps.data.id"
              @history="switchtoStudentHistory(slotProps.data)"
              @edit="switchToEditStudent(slotProps.data)"
              @delete="openDeleteStudentDialog($event)"
            />
          </div>
        </template>
        <template #noDataTemplate="slotProps">
          <AddStudentDialog
            v-if="$hasPermission(app, RightsEnum.ADD) && totalRecords === 0"
            @add="switchToAddStudent"
          />
          <NoData v-else :text="slotProps.noDataMessage" />
        </template>
      </ExpandableTable>
      <AddEditStudent
        v-else
        :is-edit="false"
        :searchQuery="searchQuery"
        :secondaryGSInfo="secondaryGSInfo"
        @cancel="switchToStudentsList"
        @submit="switchToStudentsList(true)"
      />
      <AddStudentPopup
        :searchQuery="searchQuery"
        :showAddPopup="showAddPopup"
        @update:showAddPopup="showAddPopup = $event"
        @add="switchToAddStudent"
        v-bind:studentSecondaryEdu="studentSecondaryEdu"
      />
    </div>
  </div>
</template>
<script setup lang="ts">
import NoData from "../shared/basic/NoData.vue";
import ExpandableTable from "../shared/tables/ExpandableTable.vue";
import StudentFilters from "./StudentFilters.vue";
import AddStudentDialog from "./AddStudentDialog.vue";
import AddStudentPopup from "./AddStudentPopup.vue";
import { useI18n } from "vue-i18n";
import { ref, type Ref } from "vue";
import { useRouter } from "vue-router";
import type {
  InquireStudentQuery,
  StudentListing,
  StudentData,
  StudentSecondaryEdu,
  SecondaryGSInfo,
  TableColumn,
} from "@/utils/types";
import { InquireStudentInfoProvider } from "@/providers/inquireStudentInfo";
import ViewStudentHistory from "./ViewStudentHistory.vue";
import ViewStudent from "./ViewStudent.vue";
import AddEditStudent from "./AddEditStudent.vue";
import { ConfirmDialogTypes, ApplicationEnum, RightsEnum } from "@/utils/enums";
import {
  showConfirmDialog,
  showErrorToastMessage,
  showToastMessage,
} from "@/utils/globals";
import { serverTranslate } from "@/utils/filters";

// Static Variables
const app = ApplicationEnum.STUDENT_INFO;
const tableColumns: TableColumn[] = [
  {
    field: "studentName",
    header: "studentName",
  },
  {
    field: "studentStatus__name",
    header: "studentStatus",
    statusIdField: "studentStatus_id",
  },
  {
    field: "studentNationality__name",
    header: "countryOfBirth",
  },
  {
    field: "secondary__studentSecondaryCert__name",
    header: "certificate",
  },
  {
    field: "secondary__studentCertificateYear__name",
    header: "certYear",
  },
  {
    field: "university__studentUniveristy__name",
    header: "university",
  },
  {
    field: "university__studentFaculty__name",
    header: "faculty",
  },
  {
    field: "university__studentTot",
    header: "percentage",
    suffix: "%",
  },
];

// Importing Services
const { t } = useI18n();
const router = useRouter();

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// DataTable Variables
const selected: Ref<StudentListing> = ref({});
const expandedEditRows: Ref<StudentListing[]> = ref([]);
const expandedHistoryRows: Ref<StudentListing[]> = ref([]);

// Component Data
const showAddPopup: Ref<boolean> = ref(false);
const showAddForm: Ref<boolean> = ref(false);
const searchQuery: Ref<InquireStudentQuery> = ref({});
const students: Ref<StudentListing[]> = ref([]);
const totalRecords: Ref<number> = ref(-1);
const studentSecondaryEdu: Ref<StudentSecondaryEdu> = ref({});
const secondaryGSInfo: Ref<SecondaryGSInfo> = ref({});

// Functions related to list navigation and reseting data
const clearStudentsList = (query: InquireStudentQuery) => {
  searchQuery.value = { ...query };
  students.value = [];
  totalRecords.value = -1;
  showAddForm.value = false;
};

const switchToViewStudent = (
  student: StudentListing,
  newStudentData?: StudentData
) => {
  const editIndex = expandedEditRows.value.indexOf(student);
  if (editIndex !== -1) {
    let expandedEditRowsValues = [...expandedEditRows.value];
    expandedEditRowsValues.splice(editIndex, 1);
    expandedEditRows.value = expandedEditRowsValues;
  }
  const historyIndex = expandedHistoryRows.value.indexOf(student);
  if (historyIndex !== -1) {
    let expandedHistoryRowsValues = [...expandedHistoryRows.value];
    expandedHistoryRowsValues.splice(historyIndex, 1);
    expandedHistoryRows.value = expandedHistoryRowsValues;
  }
  if (newStudentData) {
    if (newStudentData.student) {
      student.studentStatus_id =
        newStudentData.student.studentStatus_id?.toString();
      student.studentStatus__name = newStudentData.student.studentStatus__name;
      student.studentName = newStudentData.student.studentName;
      student.studentNationality__name =
        newStudentData.student.studentNationality__name;
    }
    if (newStudentData.studentDegreePercentage) {
      student.university__studentTot =
        newStudentData.studentDegreePercentage?.toString();
    }
    if (newStudentData.studentSecondaryEdu) {
      student.secondary__studentSecondaryCert__name =
        newStudentData.studentSecondaryEdu.studentSecondaryCert__name?.toString();
      student.secondary__studentCertificateYear__name =
        newStudentData.studentSecondaryEdu.studentCertificateYear__name?.toString();
    }
    if (newStudentData.studentUniversityEdu) {
      student.university__studentUniveristy__name =
        newStudentData.studentUniversityEdu?.studentUniveristy__name?.toString();
      student.university__studentFaculty__name =
        newStudentData.studentUniversityEdu?.studentFaculty__name?.toString();
    }
  }
};

const switchtoStudentHistory = (student: StudentListing) => {
  expandedHistoryRows.value = [...expandedHistoryRows.value, student];
};

const switchToEditStudent = (student: StudentListing) => {
  expandedEditRows.value = [...expandedEditRows.value, student];
};

const switchToAddStudent = (data: SecondaryGSInfo) => {
  if (data) {
    secondaryGSInfo.value = data;
    showAddForm.value = true;
  } else if (searchQuery.value.nationalID) {
    secondaryGSInfo.value = {};
    studentSecondaryEdu.value = {};
    showAddPopup.value = true;
  } else {
    showAddForm.value = true;
  }
};

const switchToStudentsList = async (reload = false) => {
  showAddForm.value = false;
  if (reload) {
    await getStudentsList(searchQuery.value);
  }
};

const openDeleteStudentDialog = (student: { studentName: string }) => {
  const deleteMessage = [
    t("deletePart1"),
    serverTranslate(student.studentName),
    t("deletePart2"),
  ].join(" ");
  selected.value = student;
  showConfirmDialog(deleteMessage, deleteStudent, ConfirmDialogTypes.CRITICAL);
};

// Function related to getting data from the back
const getStudentsList = async (
  query: InquireStudentQuery,
  resetPage = true
) => {
  isLoading.value = true;
  errorMessage.value = "";
  if (resetPage) {
    query.page = 0;
  }
  clearStudentsList(query);
  try {
    const result = await InquireStudentInfoProvider.getStudentsList(
      searchQuery.value
    );
    students.value = result.payload.studentsList;
    totalRecords.value = result.payload.totalRecords;
    router.replace({ query: { ...searchQuery.value } });
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const deleteStudent = async (confirm: boolean) => {
  if (confirm && selected.value.id) {
    try {
      const result = await InquireStudentInfoProvider.deleteStudent(
        selected.value.id
      );
      showToastMessage(result.detail);
    } catch (error) {
      showErrorToastMessage(error);
    }
    getStudentsList(searchQuery.value);
  }
};
</script>
<style scoped lang="scss">
.check-logo {
  padding: 6px;
  font-size: 1.5rem;
}
.container {
  width: 100%;
  height: 100%;
}
.confirm-card {
  width: 100%;
  height: 100%;
  overflow: auto;
  padding: 8vh;
}
.search-btn {
  height: 47px;
  line-height: 1;
}
.p-dropdown {
  position: relative;
}
@media (max-width: 300px) {
  .lang-ar .search-btn {
    font-size: 0.85rem;
  }
}

::v-deep(.p-component-ar) {
  direction: rtl !important;
  text-align: right !important;
}

::v-deep(.p-datatable.p-datatable-hoverable-rows
    .p-datatable-tbody
    > tr.p-datatable-row-expansion:not(.p-highlight):hover) {
  background-color: var(--surface-a) !important;
  color: #495057;
}
</style>
