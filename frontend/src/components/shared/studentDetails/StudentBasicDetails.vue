<template>
  <h4 class="mt-2 mb-2 mx-2">
    {{ $t("studentData") }}
  </h4>
  <div class="view-container">
    <LabeledValue
      label="studentName"
      :value="props.studentData.studentName"
      :serverTranslate="true"
    />
    <LabeledValue
      label="countryOfBirth"
      :value="props.studentData.studentNationality__name"
      :serverTranslate="true"
    />
    <LabeledValue
      v-if="
        !props.studentData.studentNationality_id ||
        props.studentData.studentNationality_id === 1
      "
      label="nationalID"
      :value="props.studentData.studentNID"
    />
    <LabeledValue
      v-if="
        props.studentData.studentNationality_id &&
        props.studentData.studentNationality_id !== 1
      "
      label="passport"
      :value="props.studentData.studentPassport"
    />
    <LabeledValue
      label="gender"
      :value="props.studentData.studentGender__name"
      :serverTranslate="true"
    />
    <LabeledValue
      label="dateOfBirth"
      :value="props.studentData.studentBirthDate"
    />
    <LabeledValue
      label="placeOfBirth"
      :value="props.studentData.studentBirthPlaceGov__name"
      :serverTranslate="true"
    />
    <LabeledValue
      label="religion"
      :value="props.studentData.studentReligion__name"
      :serverTranslate="true"
    />
    <LabeledValue
      label="residency"
      :value="props.studentData.studentAddressPlaceGov__name"
      :serverTranslate="true"
    />
    <LabeledValue label="address" :value="props.studentData.studentAddress" />
    <LabeledValue label="phone" :value="props.studentData.studentPhone" />
    <LabeledValue label="emailInput" :value="props.studentData.studentMail" />
    <LabeledValue
      label="studentStatus"
      :value="props.studentData.studentStatus__name"
      :serverTranslate="true"
    />
    <LabeledValue
      v-if="props.studentData.studentStatus_id == StudentStatus.WITHDRAWN"
      label="withdrawalDate"
      :value="props.studentData.withdrawalDate"
    />
    <LabeledValue
      label="notes"
      :value="props.studentData.notes"
      :serverTranslate="true"
    />
  </div>
</template>

<script setup lang="ts">
import type { PropType } from "vue";
import LabeledValue from "../../shared/basic/LabeledValue.vue";
import type { Student } from "@/utils/types";
import { StudentStatus } from "@/utils/enums";

const props = defineProps({
  studentData: {
    type: Object as PropType<Student>,
    default: () => {
      return {};
    },
  },
});
</script>

<style scoped lang="scss"></style>
