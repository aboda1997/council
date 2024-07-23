<template>
  <StudentFilters
    :initQuery="initQuery"
    :provider="TransferStudentsProvider"
    :simpleSearchFields="simpleSearchFields"
    :advancedSearchFields="advancedSearchFields"
    simpleSearchFieldsClasses="columns-3"
    advancedSearchFieldsClasses="columns-4"
  ></StudentFilters>
</template>
<script setup lang="ts">
import StudentFilters from "../shared/filters/StudentFilters.vue";
import { TransferStudentsProvider } from "@/providers/transferStudents";

// Static Values
const initQuery = {};
const simpleSearchFields = ["studentStatus", "nationalID", "studentName"];
const advancedSearchFields = [
  "region",
  "semester",
  "stage",
  "certificate",
  "seatNumber",
  "passport",
  "registrationType",
  "universityYear",
  "university",
  "faculty",
  "gsYear",
];
</script>
<style scoped></style>
