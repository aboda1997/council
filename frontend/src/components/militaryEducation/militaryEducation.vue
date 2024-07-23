<template>
  <div class="p-app-container">
    <div class="p-card p-app-card flex flex-column">
      <MilitaryEduFilters
        @search="getStudentsList"
        @clear="clearStudentsList"
      />
      <div class="p-seperator"></div>
      <PageLoader
        v-if="isLoading || errorMessage"
        class="flex-grow-1"
        :loading="isLoading"
        :error="errorMessage"
      />
      <NoData v-else-if="totalRecords === -1" text="" icon="" />

      <DataTable
        v-else-if="students.length"
        class="flex-grow-1"
        :paginator="showPaginator"
        :rows="searchQuery.perPage || 10"
        :rowsPerPageOptions="[10, 20, 50]"
        :totalRecords="totalRecords"
        @page="selectPage"
        :lazy="true"
        :loading="isLoading"
        selectionMode="single"
        paginatorTemplate="CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
        :value="students"
        @row-click="toggleRowExpand"
        @row-expand="setSelectedRow"
        @row-collapse="setSelectedRow"
        v-model:expandedRows="expandedRows"
        v-model:selection="selected"
        v-model:first="first"
        dataKey="id"
        responsiveLayout="stack"
        :current-page-report-template="dataTableMsg"
      >
        <Column :expander="true" headerStyle="width: 3rem" />
        <Column field="studentName" :header="$t('nationalID')">
          <template #body="slotProps">
            {{ slotProps.data.studentNID ? slotProps.data.studentNID : "‎" }}
          </template>
        </Column>
        <Column field="studentName" :header="$t('studentName')">
          <template #body="slotProps">
            {{
              slotProps.data.studentName
                ? $serverTranslate(slotProps.data.studentName)
                : "‎"
            }}
          </template>
        </Column>
        <Column
          field="secondary__studentSecondaryCert__name"
          :header="$t('certificate')"
        >
          <template #body="slotProps">
            {{
              slotProps.data.secondary__studentSecondaryCert__name
                ? $serverTranslate(
                    slotProps.data.secondary__studentSecondaryCert__name
                  )
                : "‎"
            }}
          </template>
        </Column>
        <Column
          field="secondary__studentCertificateYear__name"
          :header="$t('certYear')"
        >
          <template #body="slotProps">
            {{
              slotProps.data.secondary__studentCertificateYear__name
                ? $serverTranslate(
                    slotProps.data.secondary__studentCertificateYear__name
                  )
                : "‎"
            }}
          </template>
        </Column>
        <Column
          field="university__studentUniveristy__name"
          :header="$t('university')"
        >
          <template #body="slotProps">
            {{
              slotProps.data.university__studentUniveristy__name
                ? $serverTranslate(
                    slotProps.data.university__studentUniveristy__name
                  )
                : "‎"
            }}
          </template>
        </Column>
        <Column
          field="university__studentFaculty__name"
          :header="$t('faculty')"
        >
          <template #body="slotProps">
            {{
              slotProps.data.university__studentFaculty__name
                ? $serverTranslate(
                    slotProps.data.university__studentFaculty__name
                  )
                : "‎"
            }}
          </template>
        </Column>
        <Column
          field="military__militaryEduYear_id"
          :header="$t('simpleStatus')"
        >
          <template #body="slotProps">
            {{
              slotProps.data.military__militaryEduYear_id
                ? $t("performed")
                : $t("notPerformed")
            }}
          </template>
        </Column>
        <template #expansion="slotProps">
          <div class="flex flex-column">
            <AddEditMilitaryEdu
              v-if="
                slotProps.data &&
                !slotProps.data.military__militaryEduYear_id &&
                $hasPermission(app, RightsEnum.ADD)
              "
              :is-edit="false"
              :studentId="slotProps.data.id"
              @cancel="switchToViewStudent(slotProps.data)"
              @submit="switchToViewStudent(slotProps.data, $event)"
            />
            <AddEditMilitaryEdu
              v-else-if="
                expandedEditRows.indexOf(slotProps.data) !== -1 &&
                $hasPermission(app, RightsEnum.EDIT)
              "
              :is-edit="true"
              :studentId="slotProps.data.id"
              @cancel="switchToViewStudent(slotProps.data)"
              @submit="switchToViewStudent(slotProps.data, $event)"
            />
            <ViewMilitaryEdu
              v-else
              :studentId="slotProps.data.id"
              @edit="switchToEditStudent(slotProps.data)"
              @delete="openDeleteStudentDialog(slotProps.data)"
            />
          </div>
        </template>
      </DataTable>
      <NoData v-else text="studentsNotFound" />
    </div>
  </div>
</template>
<script setup lang="ts">
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import NoData from "../shared/basic/NoData.vue";
import PageLoader from "../shared/basic/PageLoader.vue";
import MilitaryEduFilters from "./MilitaryEduFilters.vue";
import ViewMilitaryEdu from "./ViewMilitaryEdu.vue";
import AddEditMilitaryEdu from "./AddEditMilitaryEdu.vue";
import { useI18n } from "vue-i18n";
import { ref, computed, type Ref } from "vue";
import { useRouter } from "vue-router";
import type {
  InquireStudentQuery,
  StudentListing,
  StudentMilitaryEdu,
} from "@/utils/types";
import { MilitaryEducationProvider } from "@/providers/militaryEducation";
import { ApplicationEnum, ConfirmDialogTypes, RightsEnum } from "@/utils/enums";
import {
  showConfirmDialog,
  showErrorToastMessage,
  showToastMessage,
} from "@/utils/globals";
import { serverTranslate } from "@/utils/filters";

// Static Variables
const app = ApplicationEnum.MILITARY_EDUCATION;

// Importing Services
const { t } = useI18n();
const router = useRouter();

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// Search Form Variables
const searchQuery: Ref<InquireStudentQuery> = ref({
  page: 0,
  perPage: 10,
});

//DataTable Variables
const showPaginator: Ref<boolean> = ref(true);
const first: Ref<number> = ref(0);
const selected: Ref<StudentListing> = ref({});
const expandedRows: Ref<StudentListing[]> = ref([]);
const expandedEditRows: Ref<StudentListing[]> = ref([]);

// Component Data
const students: Ref<StudentListing[]> = ref([]);
const totalRecords: Ref<number> = ref(-1);

// Custom Variables
const dataTableMsg = computed(() => {
  return "{first} " + t("to") + " {last} " + t("from") + " {totalRecords}";
});

// Functions related to list navigation and reseting data
const clearStudentsList = () => {
  selected.value = {};
  students.value = [];
  expandedRows.value = [];
  expandedEditRows.value = [];
  totalRecords.value = -1;
  searchQuery.value = {
    page: 0,
    perPage: 10,
  };
};

const selectPage = async (event: {
  page: number;
  rows: number;
  first: number;
}) => {
  if (searchQuery.value.perPage !== event.rows) {
    searchQuery.value.page = 0;
    first.value = 0;
  } else {
    searchQuery.value.page = event.page;
    first.value = event.first;
  }
  searchQuery.value.perPage = event.rows;
  getStudentsList(searchQuery.value);
};

const toggleRowExpand = (event: { data: StudentListing }) => {
  const index = expandedRows.value.indexOf(event.data);
  if (index !== -1) {
    let expandedRowsValues = expandedRows.value.filter(
      (expandedRow) => expandedRow.id !== event.data.id
    );
    expandedRows.value = expandedRowsValues;
  } else {
    expandedRows.value = [...expandedRows.value, event.data];
  }
};

const setSelectedRow = (event: { data: StudentListing }) => {
  selected.value = event.data;
};

const switchToViewStudent = (
  student: StudentListing,
  studentMilitaryEdu?: StudentMilitaryEdu
) => {
  const index = expandedEditRows.value.indexOf(student);
  if (index !== -1) {
    let expandedEditRowsValues = [...expandedEditRows.value];
    expandedEditRowsValues.splice(index, 1);
    expandedEditRows.value = expandedEditRowsValues;
  }
  if (studentMilitaryEdu) {
    student.military__militaryEduYear_id =
      studentMilitaryEdu.militaryEduYear_id;
  }
};

const switchToEditStudent = (student: StudentListing) => {
  expandedEditRows.value = [...expandedEditRows.value, student];
};

const openDeleteStudentDialog = (student: StudentListing) => {
  const deleteMessage = [
    t("deleteMiliaryEduPart1"),
    serverTranslate(student.studentName || ""),
    t("deleteMiliaryEduPart2"),
  ].join(" ");
  selected.value = student;
  showConfirmDialog(deleteMessage, deleteStudent, ConfirmDialogTypes.CRITICAL);
};

// Function related to getting data from the back
const getStudentsList = async (
  query: InquireStudentQuery,
  resetFlag?: boolean
) => {
  isLoading.value = true;
  errorMessage.value = "";
  clearStudentsList();
  if (resetFlag) {
    query.page = 0;
    first.value = 0;
  }
  if (query.page && query.perPage) {
    query.page = parseInt(query.page.toString());
    query.perPage = parseInt(query.perPage.toString());
    first.value = query.page * query.perPage;
  }
  searchQuery.value = { ...searchQuery.value, ...query };
  try {
    const result = await MilitaryEducationProvider.getStudentsList(
      searchQuery.value
    );
    students.value = result.payload.studentsList;
    totalRecords.value = result.payload.totalRecords;

    showPaginator.value = totalRecords.value > 10;
    // Fixes error when removing paginator then showing it again (per page value was not selected)
    searchQuery.value.perPage = parseInt((query.perPage || "10").toString());
    router.replace({ query: { ...searchQuery.value } });
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const deleteStudent = async (confirm: boolean) => {
  if (confirm && selected.value.id) {
    try {
      const result = await MilitaryEducationProvider.deleteStudentData(
        selected.value.id
      );
      const student = students.value.find(
        (student) => student.id == selected.value.id
      );
      if (student) {
        student.military__militaryEduYear_id = undefined;
      }
      showToastMessage(result.detail);
    } catch (error) {
      showErrorToastMessage(error);
    }
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

::v-deep(.p-datatable.p-datatable-hoverable-rows
    .p-datatable-tbody
    > tr.p-datatable-row-expansion:not(.p-highlight):hover) {
  background-color: var(--surface-a) !important;
  color: #495057;
}
</style>
