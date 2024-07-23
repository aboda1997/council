<template>
  <StudentFilters
    :initQuery="initQuery"
    :provider="ReviewGraduatesProvider"
    :simpleSearchFields="simpleSearchFields"
    :advancedSearchFields="advancedSearchFields"
    advancedSearchFieldsClasses="columns-4"
  ></StudentFilters>
</template>
<script setup lang="ts">
import StudentFilters from "../shared/filters/StudentFilters.vue";
import { ReviewGraduatesProvider } from "@/providers/reviewGraduates";

// Static Values
const initQuery = { selectedStudentType: "student" };
const simpleSearchFields = ["selectedStudentType", "nationalID", "studentName"];
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
