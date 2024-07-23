<template>
  <h4 class="mt-2 mb-2 mx-2">
    {{ $t("uniEduData") }}
  </h4>
  <div class="view-container">
    <LabeledValue
      label="enrollmentYear"
      :value="props.studentUniversityEduData.studentEnrollYear__name"
      :serverTranslate="true"
    />
    <LabeledValue
      label="enrollmentSemester"
      :value="props.studentUniversityEduData.studentEnrollSemester__name"
      :serverTranslate="true"
    />
    <LabeledValue
      label="enrollmentStage"
      :value="props.studentUniversityEduData.studentEnrollStage__name"
      :serverTranslate="true"
    />
    <LabeledValue
      label="registrationType"
      :value="props.studentUniversityEduData.studentRegistrationType__name"
      :serverTranslate="true"
    />
    <LabeledValue
      label="enrollmentUniveristy"
      :value="props.studentUniversityEduData.studentUniveristy__name"
      :serverTranslate="true"
    />
    <LabeledValue
      v-if="!isExternalUni"
      label="enrollmentFaculty"
      :value="props.studentUniversityEduData.studentFaculty__name"
      :serverTranslate="true"
    />
    <LabeledValue
      v-if="isExternalUni"
      label="enrollmentCustomExternal"
      :value="props.studentUniversityEduData.studentCustomUniversityFaculty"
      :serverTranslate="true"
    />
    <LabeledValue label="expectedGraduation" :value="expectedGraduationDate" />
  </div>
  <LabeledValue
    v-if="imposedCoursesNames"
    label="imposedCourseData"
    :value="imposedCoursesNames"
  />
</template>

<script setup lang="ts">
import type { PropType } from "vue";
import { useI18n } from "vue-i18n";
import LabeledValue from "../../shared/basic/LabeledValue.vue";
import type { StudentImposedCourse, StudentUniversityEdu } from "@/utils/types";
import { computed } from "@vue/reactivity";
import { serverTranslate } from "@/utils/filters";
import { UniversityIdEnum } from "@/utils/enums";

// Importing Services
const { t } = useI18n();

// Computed Values
const expectedGraduationDate = computed(() => {
  if (props.studentUniversityEduData) {
    return (
      (props.studentUniversityEduData.studentExpectedGraduationMonth__name
        ? serverTranslate(
            props.studentUniversityEduData.studentExpectedGraduationMonth__name
          ) + " "
        : "") +
      (props.studentUniversityEduData.studentExpectedGraduationYear__name
        ? serverTranslate(
            props.studentUniversityEduData.studentExpectedGraduationYear__name
          )
        : "")
    );
  }
  return undefined;
});
const imposedCoursesNames = computed(() => {
  if (props.studentImposedCoursesData) {
    let names = "";
    let first = true;
    for (const course of props.studentImposedCoursesData) {
      if (!first) {
        names += "\n";
      }
      names += "- " + serverTranslate(course.imposedCourse__name || "");
      if (course.completed) {
        names += " (" + t("completed") + ")";
      }
      first = false;
    }
    return names;
  }
  return " ";
});
const isExternalUni = computed(() => {
  if (props.studentUniversityEduData) {
    return (
      props.studentUniversityEduData.studentUniveristy_id ==
      UniversityIdEnum.EXTERNAL
    );
  }
  return false;
});

// Define Component Inputs (Props)
const props = defineProps({
  studentUniversityEduData: {
    type: Object as PropType<StudentUniversityEdu>,
    default: () => {
      return {};
    },
  },
  studentImposedCoursesData: {
    type: Object as PropType<StudentImposedCourse[]>,
    default: () => {
      return {};
    },
  },
});
</script>

<style scoped lang="scss"></style>
