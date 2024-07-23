<template>
  <div class="p-app-container">
    <div class="p-card p-app-card flex flex-column">
      <StudentListFilters
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
        v-model:expandedRows="expandedRows"
        v-model:selection="selected"
        v-model:first="first"
        dataKey="seating_no"
        responsiveLayout="stack"
        :current-page-report-template="dataTableMsg"
      >
        <Column :expander="true" headerStyle="width: 3rem" />
        <Column field="seating_no" :header="$t('seatNumber')"> </Column>
        <Column field="arabic_name" :header="$t('studentName')"></Column>
        <Column field="national_no" :header="$t('nationalID')"></Column>
        <Column field="city_name" :header="$t('moderia')"> </Column>

        <template #expansion="slotProps">
          <div class="flex flex-column">
            <AddEditCDStudent
              v-if="expandedEditRows.indexOf(slotProps.data) !== -1"
              :is-edit="true"
              :selected-year="slotProps.data.cert_year"
              :nationalId="slotProps.data.national_no"
              :seat-number="slotProps.data.seating_no"
              @cancel="switchToViewStudent(slotProps.data)"
              @submit="switchToViewStudent(slotProps.data, $event)"
            />
            <ViewCDStudent
              v-else
              :selected-year="slotProps.data.cert_year"
              :nationalId="slotProps.data.national_no"
              :seat-number="slotProps.data.seating_no"
              @edit="switchToEditStudent(slotProps.data)"
              @delete="openDeleteStudentDialog($event)"
            />
          </div>
        </template>
      </DataTable>
      <AddEditCDStudent
        v-else-if="showAddForm"
        :nationalId="searchQuery.search"
        @cancel="showAddForm = false"
        @submit="getStudentsList(searchQuery)"
      />
      <AddStudentDialog
        v-else-if="
          $hasPermission(app, RightsEnum.ADD) &&
          searchQuery.searchType === 'nationalID' &&
          totalRecords === 0
        "
        @add="switchToViewAddStudent"
      />
      <NoData v-else text="studentsNotFound" />
    </div>
  </div>
</template>
<script setup lang="ts">
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import ViewCDStudent from "./ViewCDStudent.vue";
import AddStudentDialog from "./AddStudentDialog.vue";
import StudentListFilters from "./StudentListFilters.vue";
import AddEditCDStudent from "./AddEditCDStudent.vue";
import NoData from "../shared/basic/NoData.vue";
import PageLoader from "../shared/basic/PageLoader.vue";
import { useI18n } from "vue-i18n";
import { ref, computed, type Ref } from "vue";
import { useRouter } from "vue-router";
import type { CDStudent, InquireCDStudentQuery } from "@/utils/types";
import { ApplicationEnum, RightsEnum, ConfirmDialogTypes } from "@/utils/enums";
import { InquireCDStudentProvider } from "@/providers/inquireCDStudent";
import {
  showConfirmDialog,
  showErrorToastMessage,
  showToastMessage,
} from "@/utils/globals";

// Importing Services
const { t } = useI18n();
const router = useRouter();

// Static Variables
const app = ApplicationEnum.INQUIRE_CD_STUDENT;

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");
const showAddForm: Ref<boolean> = ref(false);

// Search Form Variables
const searchQuery: Ref<InquireCDStudentQuery> = ref({
  selectedYear: "",
  search: "",
  page: 0,
  perPage: 10,
});

//DataTable Variables
const showPaginator: Ref<boolean> = ref(true);
const first: Ref<number> = ref(0);
const selected: Ref<CDStudent> = ref({});
const expandedRows: Ref<CDStudent[]> = ref([]);
const expandedEditRows: Ref<CDStudent[]> = ref([]);

// Component Data
const students: Ref<CDStudent[]> = ref([]);
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
  showAddForm.value = false;
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

const toggleRowExpand = (event: { data: CDStudent }) => {
  const index = expandedRows.value.indexOf(event.data);
  if (index !== -1) {
    let expandedRowsValues = expandedRows.value.filter(
      (expandedRow) => expandedRow.seating_no !== event.data.seating_no
    );
    expandedRows.value = expandedRowsValues;
  } else {
    expandedRows.value = [...expandedRows.value, event.data];
  }
};

const switchToViewAddStudent = () => {
  showAddForm.value = true;
};

const switchToViewStudent = (student: CDStudent, newStudent?: CDStudent) => {
  const index = expandedEditRows.value.indexOf(student);
  if (index !== -1) {
    let expandedEditRowsValues = [...expandedEditRows.value];
    expandedEditRowsValues.splice(index, 1);
    expandedEditRows.value = expandedEditRowsValues;
  }
  if (newStudent) {
    student.national_no = newStudent.national_no;
    student.seating_no = newStudent.seating_no;
    student.arabic_name = newStudent.arabic_name;
    student.city_name = newStudent.city_name;
  }
};

const switchToEditStudent = (student: CDStudent) => {
  expandedEditRows.value = [...expandedEditRows.value, student];
};

const openDeleteStudentDialog = (student: CDStudent) => {
  const deleteMessage = [
    t("deletePart1"),
    student.arabic_name,
    t("deletePart2"),
  ].join(" ");
  selected.value = student;
  showConfirmDialog(deleteMessage, deleteStudent, ConfirmDialogTypes.CRITICAL);
};

// Function related to getting data from the back
const getStudentsList = async (
  query: InquireCDStudentQuery,
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
    await InquireCDStudentProvider.getStudentsList(
      searchQuery.value.selectedYear,
      searchQuery.value.search,
      searchQuery.value.searchType,
      searchQuery.value.page,
      searchQuery.value.perPage
    ).then((data) => {
      students.value = data.payload.studentsList;
      totalRecords.value = data.payload.totalRecords;
    });

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
  if (confirm && selected.value.cert_year) {
    try {
      const result = await InquireCDStudentProvider.deleteStudent(
        selected.value.cert_year,
        selected.value.national_no,
        selected.value.seating_no
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
