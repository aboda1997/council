<template>
  <h4 class="mt-2 mb-2 mx-2">
    {{ $t("graduationData") }}
  </h4>
  <div class="view-container">
    <LabeledValue
      label="graduationGPA"
      :value="props.studentUniversityEduData.studentGraduationGPA"
      :serverTranslate="true"
    />
    <LabeledValue
      label="graduationGrade"
      :value="props.studentUniversityEduData.studentGraduationGrade__name"
      :serverTranslate="true"
    />
    <LabeledValue
      label="graduationPercentage"
      :value="props.studentUniversityEduData.studentGraduationPercentage"
      :serverTranslate="true"
    />
    <LabeledValue
      label="totalEquivHours"
      :value="props.studentUniversityEduData.studentGraduationEquivalentHours"
      :serverTranslate="true"
    />
    <LabeledValue
      label="enrollmentSpecialization"
      :value="props.studentUniversityEduData.studentSpecialization"
      :serverTranslate="true"
    />
    <LabeledValue
      label="enrollmentDivision"
      :value="props.studentUniversityEduData.studentDivision"
      :serverTranslate="true"
    />
    <LabeledValue
      label="graduationProjectGrade"
      :value="
        props.studentUniversityEduData.studentGraduationProjectGrade__name
      "
      :serverTranslate="true"
    />
    <LabeledValue label="actualGraduation" :value="actualGraduationDate" />
  </div>
</template>

<script setup lang="ts">
import type { PropType } from "vue";
import LabeledValue from "../../shared/basic/LabeledValue.vue";
import type { StudentUniversityEdu } from "@/utils/types";
import { computed } from "@vue/reactivity";
import { serverTranslate } from "@/utils/filters";

// Computed Values
const actualGraduationDate = computed(() => {
  if (props.studentUniversityEduData) {
    return (
      (props.studentUniversityEduData.studentActualGraduationMonth__name
        ? serverTranslate(
            props.studentUniversityEduData.studentActualGraduationMonth__name
          ) + " "
        : "") +
      (props.studentUniversityEduData.studentActualGraduationYear__name
        ? serverTranslate(
            props.studentUniversityEduData.studentActualGraduationYear__name
          )
        : "")
    );
  }
  return undefined;
});

// Define Component Inputs (Props)
const props = defineProps({
  studentUniversityEduData: {
    type: Object as PropType<StudentUniversityEdu>,
    default: () => {
      return {};
    },
  },
  showGraduationData: {
    type: Boolean,
    default: false,
  },
});
</script>

<style scoped lang="scss"></style>
