<template>
  <div class="p-app-container">
    <div class="p-card p-app-card flex flex-column">
      <StudentFilters @search="getStudentsList" @clear="clearStudentsList" />
      <div class="p-seperator"></div>
      <ExpandableTable
        :is-loading="isLoading"
        :error-message="errorMessage"
        :columns="tableColumns"
        :records="students"
        :total-records="totalRecords"
        v-bind:searchQuery="searchQuery"
        @query-change="getStudentsList(searchQuery, false)"
      >
        <template #expansion="slotProps">
          <ReviewStudentData
            v-if="
              slotProps.data.studentStatus_id ==
              StudentStatus.GRADUATION_APPLICANT
            "
            :showReviewForm="true"
            :studentId="slotProps.data.id"
            :selectedStudentType="searchQuery.selectedStudentType"
            @status-updated="getStudentsList(searchQuery)"
          />
          <ReviewStudentData
            v-else
            :studentId="slotProps.data.id"
            :selectedStudentType="searchQuery.selectedStudentType"
          />
        </template>
      </ExpandableTable>
    </div>
  </div>
</template>
<script setup lang="ts">
import StudentFilters from "./StudentFilters.vue";
import ReviewStudentData from "./ReviewStudentData.vue";
import type { InquireStudentQuery, StudentListing } from "@/utils/types";
import { type Ref, ref } from "vue";
import { useRouter } from "vue-router";
import ExpandableTable from "../shared/tables/ExpandableTable.vue";
import { ReviewGraduatesProvider } from "@/providers/reviewGraduates";
import { StudentStatus } from "@/utils/enums";

// Static Variables
const tableColumns = [
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
const router = useRouter();

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// Component Data
const searchQuery: Ref<InquireStudentQuery> = ref({});
const students: Ref<StudentListing[]> = ref([]);
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
    const result = await ReviewGraduatesProvider.getStudentsList(
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
<style scoped></style>
