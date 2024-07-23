<template>
  <h4 v-if="hasStudentMiliaryEdu" class="mt-2 mb-2 mx-2">
    {{ $t("militaryEduData") }}
  </h4>
  <div v-if="hasStudentMiliaryEdu" class="view-container">
    <LabeledValue
      label="militaryEduStatus"
      :value="
        props.studentMilitaryEduData.militaryEduGrade__name
          ? $t('performed')
          : $t('notPerformed')
      "
    />
    <LabeledValue
      label="militaryEduDate"
      :value="militaryEduDate"
      :serverTranslate="true"
    />
    <LabeledValue
      label="militaryEduGrade"
      :value="props.studentMilitaryEduData.militaryEduGrade__name"
      :serverTranslate="true"
    />
  </div>
</template>

<script setup lang="ts">
import LabeledValue from "../../shared/basic/LabeledValue.vue";
import { computed, type PropType } from "vue";
import { serverTranslate } from "@/utils/filters";
import { CountryEnum, GenderEnum } from "@/utils/enums";
import type { StudentMilitaryEdu } from "@/utils/types";

// Computed Values
const hasStudentMiliaryEdu = computed(() => {
  if (
    props.studentGenderId === GenderEnum.MALE &&
    (!props.studentNationalityId ||
      props.studentNationalityId === CountryEnum.EGYPT)
  ) {
    return true;
  }
  return false;
});
const militaryEduDate = computed(() => {
  if (props.studentMilitaryEduData) {
    return (
      (props.studentMilitaryEduData.militaryEduMonth__name
        ? serverTranslate(props.studentMilitaryEduData.militaryEduMonth__name) +
          " "
        : "") +
      (props.studentMilitaryEduData.militaryEduYear__name
        ? serverTranslate(props.studentMilitaryEduData.militaryEduYear__name)
        : "")
    );
  }
  return undefined;
});

// Define Component Inputs (Props)
const props = defineProps({
  studentMilitaryEduData: {
    type: Object as PropType<StudentMilitaryEdu>,
    default: () => {
      return {};
    },
  },
  studentGenderId: {
    type: Number,
    default: 1,
  },
  studentNationalityId: {
    type: Number,
    default: null,
  },
});
</script>

<style scoped lang="scss"></style>
