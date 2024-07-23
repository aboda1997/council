<template>
  <h4 class="mt-2 mb-2 mx-2">
    {{ $t("secEduData") }}
  </h4>
  <div class="view-container">
    <LabeledValue
      label="certificate"
      :value="props.studentSecondaryEduData.studentSecondaryCert__name"
      :serverTranslate="true"
    />
    <LabeledValue
      label="certYear"
      :value="props.studentSecondaryEduData.studentCertificateYear__name"
      :serverTranslate="true"
    />
    <LabeledValue
      label="studyGroup"
      :value="props.studentSecondaryEduData.studentStudyGroup__name"
      :serverTranslate="true"
    />
    <LabeledValue
      label="totalGrade"
      :value="props.studentSecondaryEduData.studentTot"
    />
    <LabeledValue
      v-if="!isEgyptianGeneralSecondary"
      label="totalGradeEquivalent"
      :value="props.studentSecondaryEduData.studentEquivTot"
    />
    <LabeledValue
      v-if="isEgyptianGeneralSecondary"
      label="studentSportDegree"
      :value="props.studentSecondaryEduData.studentSportDegree"
    />
    <LabeledValue
      v-if="isEgyptianGeneralSecondary"
      label="studentComplainGainDegree"
      :value="props.studentSecondaryEduData.studentComplainGain"
    />
    <LabeledValue label="totalGradePercentage" :value="totalPercentage + '%'" />
    <LabeledValue
      v-if="isEgyptianGeneralSecondary"
      label="seatNumber"
      :value="props.studentSecondaryEduData.studentSeatNumber"
    />
    <LabeledValue
      label="fulFillment"
      :value="props.studentSecondaryEduData.studentFulfillment__name"
      :serverTranslate="true"
    />
  </div>
</template>

<script setup lang="ts">
import LabeledValue from "../../shared/basic/LabeledValue.vue";
import { computed, type PropType } from "vue";
import { CertificateEnum, TotalEquivDegree } from "@/utils/enums";
import type { StudentSecondaryEdu } from "@/utils/types";

// Computed Values
const isEgyptianGeneralSecondary = computed(
  () =>
    props.studentSecondaryEduData.studentSecondaryCert_id ===
    CertificateEnum.EGYPTIAN_GENERAL_SECONADARY
);

const totalPercentage = computed(() => {
  if (
    props.studentSecondaryEduData &&
    isEgyptianGeneralSecondary.value &&
    props.studentSecondaryEduData.studentTot
  ) {
    let sportDegree = props.studentSecondaryEduData.studentSportDegree || 0;
    let complainGainDegree =
      props.studentSecondaryEduData.studentComplainGain || 0;
    let total =
      +Number(props.studentSecondaryEduData.studentTot) +
      +Number(sportDegree) +
      +Number(complainGainDegree);
    return Math.round(((total * 100) / TotalEquivDegree) * 100) / 100;
  } else if (props.studentSecondaryEduData?.studentEquivTot) {
    return (
      Math.round(
        ((props.studentSecondaryEduData.studentEquivTot * 100) /
          TotalEquivDegree) *
          100
      ) / 100
    );
  }
  return 0;
});

// Define Component Inputs (Props)
const props = defineProps({
  studentSecondaryEduData: {
    type: Object as PropType<StudentSecondaryEdu>,
    default: () => {
      return {};
    },
  },
  studentStatusId: {
    type: Number,
    default: 1,
  },
});
</script>

<style scoped lang="scss"></style>
