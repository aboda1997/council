<template>
  <div class="print-bar">
    <div v-if="props.showColumnsField" class="field mt-4 mb-2 mx-2">
      <span class="p-float-label">
        <InputNumber
          id="maxColumnsPerTable"
          class="w-full"
          type="text"
          :useGrouping="false"
          :min="1"
          :max="props.totalColumns"
          v-model="maxColumnsPerTable"
          showButtons
        />
        <label for="maxColumnsPerTable">{{ $t("maxColumnsPerTable") }} </label>
      </span>
    </div>

    <div v-if="props.showRowsField" class="field mt-4 mb-2 mx-2">
      <span class="p-float-label">
        <InputNumber
          id="maxRowsPerTable"
          class="w-full"
          type="text"
          :useGrouping="false"
          :min="1"
          :max="props.TotalNumOfRows"
          v-model="maxRowsPerTable"
          showButtons
        />
        <label for="maxRowsPerTable">{{ $t("maxNumOfRowsText") }} </label>
      </span>
    </div>

    <div
      class="button-bar"
      :class="props.showColumnsField || props.showRowsField ? '' : 'w-full'"
    >
      <Button
        :label="$t('export')"
        icon="pi pi-file-excel icon-fix"
        class="print-btn p-button p-button-primary m-2"
        :loading="isLoadingExcel"
        @click="exportExcel()"
      />
      <Button
        :label="$t('print')"
        icon="pi pi-print icon-fix"
        class="print-btn p-button p-button-secondary my-2"
        :loading="isLoadingPrint"
        @click="print()"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import Button from "primevue/button";
import InputNumber from "primevue/inputnumber";
import { computed, ref } from "vue";
import { exportExcelHtmlElement, printVueHtmlElement } from "@/utils/filters";

const isLoadingPrint = ref(false);
const isLoadingExcel = ref(false);

const maxColumnsPerTable = computed({
  get: () => props.maxColumnsPerTable,
  set: (value) => emit("update:maxColumnsPerTable", value),
});

const maxRowsPerTable = computed({
  get: () => props.maxRowsPerTable,
  set: (value) => emit("update:maxRowsPerTable", value),
});

const props = defineProps({
  printableElement: { type: String, default: "print-me" },
  exportFileName: { type: String, default: "CPNU-Report" },
  showColumnsField: { type: Boolean, default: false },
  showRowsField: { type: Boolean, default: false },
  maxColumnsPerTable: { type: Number, default: 0 },
  totalColumns: { type: Number, default: 100 },
  maxRowsPerTable: { type: Number, default: 20 },
  totalRows: { type: Number, default: 20 },
  TotalNumOfRows: { type: Number, default: 20 },
});

const emit = defineEmits([
  "update:maxColumnsPerTable",
  "update:maxRowsPerTable",
]);

// Print printable Element
const exportExcel = () => {
  // Get HTML to print from element
  isLoadingExcel.value = true;
  exportExcelHtmlElement(props.printableElement, props.exportFileName);
  isLoadingExcel.value = false;
};

const print = () => {
  // Get HTML to print from element
  isLoadingPrint.value = true;
  printVueHtmlElement(props.printableElement);
  isLoadingPrint.value = false;
};
</script>

<style lang="scss">
.print-bar {
  display: flex;
  align-items: center;
  background-color: #e9ecefc0;
  border-radius: 1rem;
  padding: 0 10px;
  margin: 10px;
  @media print {
    display: none;
  }
  .p-inputtext {
    padding: 0.25rem 0.75rem;
  }
}
.button-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-inline-start: auto;
}
</style>
