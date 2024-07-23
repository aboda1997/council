<template>
  <StudentFilters
    :initQuery="initQuery"
    :provider="ReviewInitiallyAcceptedProvider"
    :simpleSearchFields="simpleSearchFields"
    :advancedSearchFields="advancedSearchFields"
    simpleSearchFieldsClasses="columns-2"
    advancedSearchFieldsClasses="columns-4"
  ></StudentFilters>
</template>
<script setup lang="ts">
import StudentFilters from "../shared/filters/StudentFilters.vue";
import { ReviewInitiallyAcceptedProvider } from "@/providers/reviewInitiallyAccepted";

// Static Values
const initQuery = {};
const simpleSearchFields = ["nationalID", "studentName"];
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
