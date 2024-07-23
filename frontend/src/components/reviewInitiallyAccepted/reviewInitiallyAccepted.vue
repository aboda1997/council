<template>
  <div class="p-app-container">
    <div class="p-card p-app-card flex flex-column">
      <StudentFilters @search="getStudentsList" @clear="clearStudentsList" />
      <div class="p-seperator"></div>
      <SimpleTable
        :is-loading="isLoading"
        :error-message="errorMessage"
        :columns="tableColumns"
        :records="students"
        :total-records="totalRecords"
        :show-selector="true"
        selection-mode="multiple"
        v-bind:searchQuery="searchQuery"
        @selected-updated="selected = $event"
        @query-change="getStudentsList(searchQuery, false)"
      >
      </SimpleTable>
    </div>
    <div class="p-card form-card" v-if="$hasPermission(app, RightsEnum.EDIT)">
      <ReviewStudentData
        :selected-students="selected"
        @submit="getStudentsList(searchQuery)"
      />
    </div>
  </div>
</template>
<script setup lang="ts">
import SimpleTable from "../shared/tables/SimpleTable.vue";
import StudentFilters from "./StudentFilters.vue";
import ReviewStudentData from "./ReviewStudentData.vue";
import { type Ref, ref } from "vue";
import { useRouter } from "vue-router";
import type { InquireStudentQuery, StudentListing } from "@/utils/types";
import { ReviewInitiallyAcceptedProvider } from "@/providers/reviewInitiallyAccepted";
import { ApplicationEnum, RightsEnum } from "@/utils/enums";

// Static Variables
const app = ApplicationEnum.REVIEW_INITIALLY_ACCEPTED;
const tableColumns = [
  {
    field: "studentName",
    header: "studentName",
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
const router = useRouter();

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// Component Data
const searchQuery: Ref<InquireStudentQuery> = ref({});
const students: Ref<StudentListing[]> = ref([]);
const selected: Ref<StudentListing[]> = ref([]);
const totalRecords: Ref<number> = ref(-1);

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
    const result = await ReviewInitiallyAcceptedProvider.getStudentsList(
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

const clearStudentsList = (query: InquireStudentQuery) => {
  searchQuery.value = { ...query };
  students.value = [];
  totalRecords.value = -1;
};
</script>
<style scoped>
.form-card {
  margin: 0.75rem;
  padding: 0.75rem;
}
</style>
