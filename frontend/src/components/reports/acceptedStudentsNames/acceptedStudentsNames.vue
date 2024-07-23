<template>
  <div class="p-app-container printable">
    <div class="p-card p-app-card flex flex-column">
      <ReportFilters
        @search="getReportData"
        @clear="clearReportData"
        @filters="responseFilters = $event"
      />
      <div class="p-seperator"></div>

      <PageLoader
        v-if="isLoading || errorMessage"
        class="flex-grow-1"
        :loading="isLoading"
        :error="errorMessage"
      />
      <div id="printable-report" v-else-if="data && data.length">
        <PrintBar
          printable-element="printable-report"
          :totalColumns="columns.length + 1"
          :showRowsField="true"
          :TotalNumOfRows="data.length"
          v-model:maxColumnsPerTable="maxColumnsPerTable"
          v-model:maxRowsPerTable="maxRowsPerTable"
        />

        <div
          class="report-container"
          v-for="index in Math.ceil(data.length / maxRowsPerTable)"
          :key="index"
        >
          <table>
            <thead>
              <tr>
                <!--This is the header with university logo-->
                <th :colspan="columns.length + 1">
                  <ReportHeader :reportDetails="reportDetails" />
                </th>
              </tr>

              <tr>
                <th>{{ $t("num") }}</th>
                <th v-for="column in columns" :key="column">
                  {{ $t(column) }}
                </th>
              </tr>
            </thead>

            <tbody>
              <template
                v-for="(row, num) in getTableRows(index)"
                :key="row.univ_id"
              >
                <tr>
                  <td>{{ (index - 1) * maxRowsPerTable + num + 1 }}</td>
                  <template v-for="field in columns" :key="field.id">
                    <td>
                      {{ $serverTranslate(String(row[field] || "")) }}
                    </td>
                  </template>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>
      <NoData v-else-if="reportLoaded" />
      <NoData v-else text="" icon="" />
    </div>
  </div>
</template>
<script setup lang="ts">
import NoData from "../../shared/basic/NoData.vue";
import PrintBar from "../../shared/basic/PrintBar.vue";
import PageLoader from "../../shared/basic/PageLoader.vue";
import ReportHeader from "../../shared/basic/ReportHeader.vue";
import ReportFilters from "./ReportFilters.vue";
import { computed, ref, type Ref } from "vue";
import { useRouter } from "vue-router";
import type {
  CouncilFilters,
  AcceptedStudentsNamesData,
  ReportStudentsQuery,
} from "@/utils/types";
import { AcceptedStudentsNamesProvider } from "@/providers/reports/acceptedStudentsNames";
import { serverTranslate } from "@/utils/filters";

// Importing Services
const router = useRouter();

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// Search Form Variables
const responseFilters: Ref<CouncilFilters> = ref({});
const searchQuery: Ref<ReportStudentsQuery> = ref({});

// Report Data
const reportLoaded: Ref<boolean> = ref(false);
const data: Ref<AcceptedStudentsNamesData[]> = ref([]);
const columns: Ref<string[]> = ref([]);

// Component Data
const maxColumnsPerTable: Ref<number> = ref(9);
const maxRowsPerTable: Ref<number> = ref(20);

const reportDetails = computed(() => {
  let reportDetailsString = "";
  const univName =
    responseFilters.value.universities?.find(
      (university) =>
        university.id.toString() === searchQuery.value.university?.toString()
    )?.name || "";
  reportDetailsString += serverTranslate(univName);
  const yearName =
    responseFilters.value.years?.find(
      (year) => year.id.toString() === searchQuery.value.year?.toString()
    )?.name || "";
  reportDetailsString += ", ";
  if (yearName) {
    reportDetailsString += serverTranslate(yearName);
  } else {
    reportDetailsString += serverTranslate("كل الأعوام|All Years");
  }
  console.log(searchQuery.value);
  const semesterName =
    responseFilters.value.semesters?.find(
      (semester) =>
        semester.id.toString() === searchQuery.value.semester?.toString()
    )?.name || "";
  if (semesterName) {
    reportDetailsString += ", ";
    reportDetailsString += serverTranslate(semesterName);
  }
  const stageName =
    responseFilters.value.stages?.find(
      (stage) => stage.id.toString() === searchQuery.value.stage?.toString()
    )?.name || "";
  if (stageName) {
    reportDetailsString += ", ";
    reportDetailsString += serverTranslate(stageName);
  }
  const studentStatusName =
    responseFilters.value.status?.find(
      (studentStatus) =>
        studentStatus.id.toString() ===
        searchQuery.value.studentStatus?.toString()
    )?.name || "";
  if (studentStatusName) {
    reportDetailsString += ", ";
    reportDetailsString += serverTranslate(studentStatusName);
  }
  const fulfillmentName =
    responseFilters.value.fulfillments?.find(
      (fulfillment) =>
        fulfillment.id.toString() === searchQuery.value.fulfillment?.toString()
    )?.name || "";
  if (fulfillmentName) {
    reportDetailsString += ", ";
    reportDetailsString += serverTranslate(fulfillmentName);
  }
  const regionName =
    responseFilters.value.countries?.find(
      (region) => region.id.toString() === searchQuery.value.region?.toString()
    )?.name || "";
  if (regionName) {
    reportDetailsString += ", ";
    reportDetailsString += serverTranslate(regionName);
  }
  const certificateName =
    responseFilters.value.certificates?.find(
      (certificate) =>
        certificate.id.toString() === searchQuery.value.certificate?.toString()
    )?.name || "";
  if (certificateName) {
    reportDetailsString += ", ";
    reportDetailsString += serverTranslate(certificateName);
  }
  const gsYearName =
    responseFilters.value.years?.find(
      (gsYear) => gsYear.id.toString() === searchQuery.value.gsYear?.toString()
    )?.name || "";
  if (gsYearName) {
    reportDetailsString += ", ";
    reportDetailsString += serverTranslate(gsYearName);
  }
  const registrationTypeName =
    responseFilters.value.registrationTypes?.find(
      (registrationType) =>
        registrationType.id.toString() ===
        searchQuery.value.registrationType?.toString()
    )?.name || "";
  if (registrationTypeName) {
    reportDetailsString += ", ";
    reportDetailsString += serverTranslate(registrationTypeName);
  }
  return reportDetailsString;
});

const getTableRows = (rowNumber: number) => {
  if (rowNumber > 0) {
    return data.value.slice(
      (rowNumber - 1) * maxRowsPerTable.value,
      rowNumber * maxRowsPerTable.value
    );
  }
  return data.value;
};

// Functions related to list navigation and reseting data
const clearReportData = () => {
  reportLoaded.value = false;
  data.value = [];
  columns.value = [];
  searchQuery.value = {};
};

// Function related to getting data from the back
const getReportData = async (query: ReportStudentsQuery) => {
  isLoading.value = true;
  errorMessage.value = "";
  clearReportData();
  searchQuery.value = { ...searchQuery.value, ...query };
  const reportParams = { ...searchQuery.value };
  try {
    const result = await AcceptedStudentsNamesProvider.getReportData(
      reportParams
    );
    columns.value = result.payload.columns;
    data.value = result.payload.reportData;
    reportLoaded.value = true;

    // Fixes error when removing paginator then showing it again (per page value was not selected)
    router.replace({ query: { ...searchQuery.value } });
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
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
