<template>
  <StudentFilters
    :initQuery="{}"
    :provider="MilitaryEducationProvider"
    :simpleSearchFields="simpleSearchFields"
    :advancedSearchFields="advancedSearchFields"
    advancedSearchFieldsClasses="columns-3"
  ></StudentFilters>
</template>
<script setup lang="ts">
import StudentFilters from "../shared/filters/StudentFilters.vue";
import { MilitaryEducationProvider } from "@/providers/militaryEducation";

// Static Values
const simpleSearchFields = ["nationalID", "studentName"];
const advancedSearchFields = ["university", "faculty", "militaryStatusType"];
</script>
<style scoped></style>
