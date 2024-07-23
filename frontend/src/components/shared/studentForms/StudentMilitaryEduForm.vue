<template>
  <div class="form-container">
    <div class="field mt-3 mx-2">
      <span class="p-float-label">
        <InputText
          id="militaryEduStatus"
          class="w-full p-inputwrapper-filled"
          type="text"
          :value="
            studentMilitaryEdu.militaryEduGrade__name
              ? $t('performed')
              : $t('notPerformed')
          "
          :disabled="true"
        />
        <label for="militaryEduStatus">{{ $t("militaryEduStatus") }} </label>
      </span>
    </div>
    <div class="field mt-3 mx-2" v-if="studentMilitaryEdu.militaryEduYear_id">
      <span class="p-float-label">
        <InputText
          id="militaryEduYear"
          class="w-full"
          type="text"
          :value="
            $serverTranslate(studentMilitaryEdu.militaryEduYear__name || '')
          "
          :disabled="true"
          optionLabel="translatedName"
        />
        <label for="militaryEduYear">{{ $t("militaryEduYear") }} </label>
      </span>
    </div>
    <div class="field mt-3 mx-2" v-if="studentMilitaryEdu.militaryEduGrade_id">
      <span class="p-float-label">
        <InputText
          id="militaryEduGrade"
          class="w-full"
          type="text"
          :value="
            $serverTranslate(studentMilitaryEdu.militaryEduGrade__name || '')
          "
          :disabled="true"
          optionLabel="translatedName"
        />
        <label for="militaryEduGrade">{{ $t("militaryEduGrade") }} </label>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import InputText from "primevue/inputtext";
import { computed, onMounted, type PropType } from "vue";
import useVuelidate from "@vuelidate/core";
import type { StudentMilitaryEdu } from "@/utils/types";

// Computed Student Data
const studentMilitaryEdu = computed({
  get: () => props.studentMilitaryEdu,
  set: (value) => emit("update:studentMilitaryEdu", value),
});

// Define Component Inputs (Props)
const props = defineProps({
  isEdit: { type: Boolean, default: true },
  studentStatusId: {
    type: Number,
    default: -1,
  },
  studentMilitaryEdu: {
    type: Object as PropType<StudentMilitaryEdu>,
    default: null,
  },
});

// Define Component Outputs (Emits)
const emit = defineEmits(["update:studentMilitaryEdu"]);

// on mount functions
onMounted(async () => {
  if (props.isEdit) {
    await v$.value.$validate();
  }
});

// Validation Rules
const rules = {};

// Set up component Validation
const v$ = useVuelidate(rules, {});
</script>

<style scoped lang="scss"></style>
