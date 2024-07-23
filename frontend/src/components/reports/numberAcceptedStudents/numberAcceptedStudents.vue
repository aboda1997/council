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
          :showColumnsField="true"
          :totalColumns="columns.length"
          v-model:maxColumnsPerTable="maxColumnsPerTable"
        />
        <div
          class="report-container"
          v-for="index in numberOfTables"
          :key="index"
        >
          <table>
            <thead>
              <tr>
                <th :colspan="getTableColumns(index).length * 2 + 1">
                  <ReportHeader :reportDetails="reportDetails" />
                </th>
              </tr>
              <tr>
                <th rowspan="2">-</th>
                <template
                  v-for="column in getTableColumns(index)"
                  :key="column.id"
                >
                  <th colspan="2">
                    {{ $serverTranslate(column.name) }}
                  </th>
                </template>
              </tr>
              <tr>
                <template
                  v-for="column in getTableColumns(index)"
                  :key="column.id"
                >
                  <th>
                    {{ $t("allocated") }}
                  </th>
                  <th>
                    {{ $t("accepted") }}
                  </th>
                </template>
              </tr>
            </thead>
            <tbody>
              <template v-for="row in data" :key="row.univ_id">
                <tr>
                  <td>{{ $serverTranslate(row.univ_name) }}</td>
                  <template
                    v-for="column in getTableColumns(index)"
                    :key="column.id"
                  >
                    <td class="center-v center-h">
                      {{ row[column.id + "_allocated_seats"] || "0" }}
                    </td>
                    <td class="center-v center-h">
                      {{ row[column.id + "_actual_seats"] || "0" }}
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
  ReportTableColumn,
  NumberAcceptedStudentsData,
  ReportStudentsQuery,
} from "@/utils/types";
import { NumberAcceptedStudentsProvider } from "@/providers/reports/numberAcceptedStudents";
import { serverTranslate } from "@/utils/filters";

// Static Variables
const exportFileName = "CPNU-Accepted-Student-Report";

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
const data: Ref<NumberAcceptedStudentsData[]> = ref([]);
const columns: Ref<ReportTableColumn[]> = ref([]);

// Component Data
const maxColumnsPerTable: Ref<number> = ref(6);

// Computed Values
const numberOfTables = computed(() => {
  if (maxColumnsPerTable.value > 0) {
    return Math.ceil(columns.value.length / maxColumnsPerTable.value);
  }
  return 1;
});
const reportDetails = computed(() => {
  const yearName =
    responseFilters.value.years?.find(
      (year) => year.id.toString() === searchQuery.value.year?.toString()
    )?.name || "";
  let registrationTypesName = "";
  responseFilters.value.registrationTypes
    ?.filter((type) =>
      (searchQuery.value.registrationTypes || "".split(",")).includes(
        type.id.toString() || "-1"
      )
    )
    .map((type) => {
      registrationTypesName += ", ";
      registrationTypesName += serverTranslate(type.name);
    });
  return serverTranslate(yearName) + registrationTypesName;
});

// Slices Table Columns depending on the max column and table index
const getTableColumns = (tableNumber: number) => {
  if (maxColumnsPerTable.value > 0) {
    return columns.value.slice(
      (tableNumber - 1) * maxColumnsPerTable.value,
      tableNumber * maxColumnsPerTable.value
    );
  }
  return columns.value;
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
  if (reportParams.registrationTypes) {
    reportParams.registrationTypes = reportParams.registrationTypes.toString();
  }
  try {
    const result = await NumberAcceptedStudentsProvider.getReportData(
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
