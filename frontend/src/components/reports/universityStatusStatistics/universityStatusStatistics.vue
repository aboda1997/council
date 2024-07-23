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
          :exportFileName="exportFileName"
          :totalColumns="columns.length"
          v-model:maxColumnsPerTable="maxColumnsPerTable"
        />
        <div class="report-container">
          <table>
            <thead>
              <tr>
                <th :colspan="columns.length + 3">
                  <ReportHeader :reportDetails="reportDetails" />
                </th>
              </tr>
              <tr>
                <th>-</th>
                <th>
                  {{ $t("allocated") }}
                </th>
                <template v-for="column in columns" :key="column.id">
                  <th>
                    {{ $serverTranslate(column.name) }}
                  </th>
                </template>
                <th>
                  {{ $t("remaining") }}
                </th>
              </tr>
            </thead>
            <tbody>
              <template v-for="row in data" :key="row.univ_id">
                <tr>
                  <td>{{ $serverTranslate(row.fac_type_name) }}</td>
                  <td class="center-v center-h">
                    {{ row["allocated_seats"] || "0" }}
                  </td>
                  <template v-for="column in columns" :key="column.id">
                    <td class="center-v center-h">
                      {{ row[column.id + "_actual_seats"] || "0" }}
                    </td>
                  </template>
                  <td class="center-v center-h">
                    {{ row["remaining"] || "0" }}
                  </td>
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
  ReportTableColumn,
  UniversityStatusStatisticsData,
  ReportStudentsQuery,
} from "@/utils/types";
import { UniversityStatusStatisticsProvider } from "@/providers/reports/universityStatusStatistics";
import { serverTranslate } from "@/utils/filters";

// Static Variables
const exportFileName = "CPNU-Student-Status-Report";

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
const data: Ref<UniversityStatusStatisticsData[]> = ref([]);
const columns: Ref<ReportTableColumn[]> = ref([]);

// Component Data
const maxColumnsPerTable: Ref<number> = ref(6);

// Computed Values
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
  reportDetailsString += serverTranslate(yearName);
  responseFilters.value.registrationTypes
    ?.filter((type) =>
      (searchQuery.value.registrationTypes || "".split(",")).includes(
        type.id.toString() || "-1"
      )
    )
    .map((type) => {
      reportDetailsString += ", ";
      reportDetailsString += serverTranslate(type.name);
    });
  return reportDetailsString;
});

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
  if (reportParams.registrationTypes) {
    reportParams.registrationTypes = reportParams.registrationTypes.toString();
  }
  try {
    const result = await UniversityStatusStatisticsProvider.getReportData(
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
