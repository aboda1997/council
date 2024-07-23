<template>
  <PageLoader
    v-if="props.isLoading || props.errorMessage || errorMessage"
    class="flex-grow-1"
    :loading="props.isLoading"
    :error="props.errorMessage || errorMessage"
  />
  <NoData v-else-if="totalRecords === -1" text="" icon="" />
  <DataTable
    v-else-if="records.length"
    class="flex-grow-1 simple-table"
    :paginator="showPaginator"
    :rows="searchQuery.perPage || 10"
    :rowsPerPageOptions="[10, 20, 50]"
    :value="props.records"
    :totalRecords="props.totalRecords"
    @page="updateQuery"
    @sort="updateQuery"
    :lazy="true"
    :loading="isLoading"
    :selectionMode="props.selectionMode"
    paginatorTemplate="CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
    v-model:selection="selected"
    v-model:first="first"
    dataKey="id"
    responsiveLayout="stack"
    :current-page-report-template="dataTableMsg"
    :sortField="searchQuery.sortBy"
    :sortOrder="searchQuery.sortOrder"
    removableSort
  >
    <Column
      v-if="showSelector"
      :selectionMode="props.selectionMode"
      :exportable="false"
      headerStyle="width: 3rem"
    ></Column>
    <template v-for="entry in props.columns" :key="entry">
      <Column
        :field="entry.field || ''"
        :sortable="entry.sortable || false"
        :header="$t((entry.header ? entry.header : entry.field) || '')"
      >
        <template #body="slotProps">
          <span
            :class="[
              entry.statusIdField
                ? 'table-status-chip' +
                  ' ' +
                  getStatusColor(slotProps.data[entry.statusIdField])
                : '',
            ]"
          >
            {{
              entry.field && slotProps.data[entry.field]
                ? $evaluateStringValue(entry.prefix) +
                  $serverTranslate(slotProps.data[entry.field].toString()) +
                  $evaluateStringValue(entry.suffix)
                : props.noRowDataMessage
            }}
          </span>
        </template>
      </Column>
    </template>
  </DataTable>
  <slot
    name="noDataTemplate"
    :noDataMessage="props.noDataMessage"
    v-else-if="$slots.noDataTemplate"
  ></slot>
  <NoData v-else :text="props.noDataMessage" />
</template>
<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import NoData from "../basic/NoData.vue";
import PageLoader from "../basic/PageLoader.vue";
import { useI18n } from "vue-i18n";
import { ref, computed, type Ref, type PropType, watch } from "vue";
import { StudentStatusColorMapping } from "@/utils/enums";
import type { TableColumn } from "@/utils/types";

// Importing Services
const { t } = useI18n();

// UI Variables
const errorMessage: Ref<string> = ref("");

// Component Data
const searchQuery = computed({
  get: () => props.searchQuery,
  set: (value) => emit("update:searchQuery", value),
});
const first = computed(
  () => (props.searchQuery.page || 0) * (props.searchQuery.perPage || 0)
);
const selected = computed({
  get: () => privateSelected.value,
  set: (value) => {
    privateSelected.value = value;
    emit("selectedUpdated", value);
  },
});
const showPaginator: Ref<boolean> = ref(false);
const privateSelected: Ref<any[]> = ref([]);

// Custom Variables
const dataTableMsg = computed(() => {
  return "{first} " + t("to") + " {last} " + t("from") + " {totalRecords}";
});

// Define Component Inputs (Props)
const props = defineProps({
  columns: {
    type: Array as PropType<TableColumn[]>,
    default: () => [],
  },
  records: {
    type: Array as PropType<any[]>,
    default: () => [],
  },
  totalRecords: {
    type: Number,
    default: 0,
  },
  selected: {
    type: Object as PropType<any>,
    default: null,
  },
  searchQuery: {
    type: Object as PropType<any>,
    default: null,
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
  errorMessage: {
    type: String,
    default: "",
  },
  noRowDataMessage: {
    type: String,
    default: "‎",
  },
  noDataMessage: {
    type: String,
    default: "studentsNotFound",
  },
  showSelector: {
    type: Boolean,
    default: false,
  },
  selectionMode: {
    type: Object as PropType<any>,
    default: () => {
      return "single";
    },
  },
});

// Define Component Outputs (Emits)
const emit = defineEmits([
  "update:searchQuery",
  "selectedUpdated",
  "clearRecords",
  "queryChange",
]);

// Define Component Watchers
watch(
  () => [props.totalRecords],
  () => {
    selected.value = [];
    showPaginator.value = props.totalRecords >= 10;
    // Fixes error when removing paginator then showing it again (per page value was not selected)
    searchQuery.value.perPage = parseInt(
      (searchQuery.value.perPage || "10").toString()
    );
  }
);
watch(
  () => [props.selected],
  () => {
    if (props.selected) {
      selected.value = props.selected;
    }
  }
);

// Functions related to list navigation and reseting data
const getStatusColor = (statusId: number) => {
  return StudentStatusColorMapping[
    statusId as keyof typeof StudentStatusColorMapping
  ];
};

const updateQuery = async (event: {
  page: number;
  rows: number;
  first: number;
  sortField: string;
  sortOrder: number;
}) => {
  if (searchQuery.value.perPage !== event.rows) {
    searchQuery.value.page = 0;
  } else {
    searchQuery.value.page = event.page;
  }
  if (event.sortField) {
    searchQuery.value.sortBy = event.sortField;
    searchQuery.value.sortOrder = event.sortOrder;
  } else {
    delete searchQuery.value.sortBy;
    delete searchQuery.value.sortOrder;
  }
  searchQuery.value.perPage = event.rows;
  emit("queryChange", searchQuery.value);
};

// Function related to getting data from the back
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
</style>
