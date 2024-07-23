<template>
  <NoData text="studentsNotFound">
    <p class="no-data-text no-data-text-small">
      {{ $t("addNewStudentGeneralMessage") }}
    </p>
    <div
      class="flex flex-row justify-content-center align-items-center btn-wrapper"
    >
      <Button
        :label="$t('createNewStudent')"
        class="p-button-sm"
        @click="emit('add')"
      />
    </div>
  </NoData>
</template>

<script setup lang="ts">
import Button from "primevue/button";
import NoData from "../shared/basic/NoData.vue";

// Define Component Outputs (Emits)
const emit = defineEmits(["add"]);
</script>

<style lang="scss" scoped></style>
