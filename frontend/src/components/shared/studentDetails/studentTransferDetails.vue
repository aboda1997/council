<template>
  <h4 class="mt-2 mb-2 mx-2">
    {{ $t("transferData") }}
  </h4>
  <div class="view-container">
    <LabeledValue
      label="prevEnrollmentUniveristy"
      :value="props.studentUniversityEduData.studentPrevUniveristy__name"
      :serverTranslate="true"
    />
    <LabeledValue
      v-if="!isExternalUni"
      label="prevEnrollmentFaculty"
      :value="props.studentUniversityEduData.studentPrevFaculty__name"
      :serverTranslate="true"
    />
    <LabeledValue
      v-if="isExternalUni"
      label="prevEnrollmentCustomExternal"
      :value="props.studentUniversityEduData.studentPrevCustomUniversityFaculty"
      :serverTranslate="true"
    />
    <LabeledValue
      label="prevEnrollmentYear"
      :value="props.studentUniversityEduData.studentPrevEnrollYear__name"
      :serverTranslate="true"
    />
    <LabeledValue
      label="prevEnrollmentSemester"
      :value="props.studentUniversityEduData.studentPrevEnrollSemester__name"
      :serverTranslate="true"
    />
    <LabeledValue
      label="prevEnrollmentStage"
      :value="props.studentUniversityEduData.studentPrevEnrollStage__name"
      :serverTranslate="true"
    />
    <LabeledValue
      label="transferDate"
      :value="props.studentUniversityEduData.transferDate"
      :serverTranslate="true"
    />
  </div>
  <div class="view-container">
    <LabeledValue
      label="transferLevel"
      :value="props.studentUniversityEduData.studentLevel__name"
      :serverTranslate="true"
    />
    <LabeledValue
      label="totalEquivHours"
      :value="props.studentUniversityEduData.totalEquivalentHours"
    />
    <LabeledValue
      label="fulFillmentReasons"
      :value="props.studentUniversityEduData.transferFulfillment__name"
      :serverTranslate="true"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, type PropType } from "vue";
import LabeledValue from "../../shared/basic/LabeledValue.vue";
import { UniversityIdEnum } from "@/utils/enums";
import type { StudentUniversityEdu } from "@/utils/types";

// Computed Variables
const isExternalUni = computed(() => {
  if (props.studentUniversityEduData) {
    return (
      props.studentUniversityEduData.studentPrevUniveristy_id ==
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
});
</script>

<style scoped lang="scss"></style>
