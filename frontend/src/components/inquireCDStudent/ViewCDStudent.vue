<template>
  <PageLoader
    v-if="isLoading || errorMessage"
    :loading="isLoading"
    :error="errorMessage"
  />
  <template v-else>
    <div class="flex flex-column">
      <div
        class="header grid justify-content-between px-2 pt-2 md:flex-row flex-column-reverse"
      >
        <h4 class="mt-3 mb-0 mx-2">{{ $t("studentData") }}</h4>
        <div class="button-wrapper flex md:mt-2">
          <Button
            v-if="$hasPermission(app, RightsEnum.EDIT)"
            :label="$t('edit')"
            icon="pi pi-pencil"
            class="p-button p-button-warning p-button-sm flex-grow-1 mx-2 my-auto"
            @click="editStudent()"
          />
          <Button
            v-if="$hasPermission(app, RightsEnum.DELETE)"
            :label="$t('delete')"
            icon="pi pi-trash"
            class="p-button p-button-danger p-button-sm flex-grow-1 mx-2 my-auto"
            @click="deleteStudent()"
          />
        </div>
      </div>
      <div class="view-container">
        <LabeledValue label="studentName" :value="student.arabic_name" />
        <LabeledValue label="nationalID" :value="student.national_no" />
        <LabeledValue label="seatNumber" :value="student.seating_no" />
        <LabeledValue label="tansiqNumber" :value="student.tanseq_number" />
        <LabeledValue label="nationality" :value="student.nationality_name" />
        <LabeledValue label="religion" :value="student.religion_name" />
        <LabeledValue label="gender" :value="student.gender_name" />
        <LabeledValue label="dateOfBirth" :value="student.date_of_birth" />
        <LabeledValue label="placeOfBirth" :value="student.birth_palace" />
        <LabeledValue label="barCode" :value="student.bar_code" />
      </div>
      <h4 class="mt-2 mb-2 mx-2">{{ $t("residency") }}</h4>
      <div class="view-container">
        <LabeledValue label="governorate" :value="student.governorate_name" />
        <LabeledValue label="policeStation" :value="student.police_station" />
        <LabeledValue label="address" :value="student.address" />
      </div>
      <h4 class="mt-2 mb-2 mx-2">{{ $t("eduData") }}</h4>
      <div class="view-container">
        <LabeledValue label="branch" :value="student.branch_name" />
        <LabeledValue label="educationType" :value="student.school_code_name" />
        <LabeledValue label="schoolType" :value="student.school_type_name" />
        <LabeledValue label="governorate" :value="student.city_name" />
        <LabeledValue label="adminstrationName" :value="student.dept_name" />
        <LabeledValue label="schoolName" :value="student.school_name" />
        <LabeledValue label="control" :value="student.control_name" />
        <LabeledValue label="firstLanguage" :value="student.first_lang_name" />
        <LabeledValue
          label="secondLanguage"
          :value="student.second_lang_name"
        />
      </div>

      <h4 class="mt-2 mb-3 mx-2">{{ $t("grades") }}</h4>
      <div class="table-container">
        <DataTable
          class="tiny-header centered"
          :value="[student]"
          responsiveLayout="stack"
        >
          <Column field="arabic" :header="$t('arabic')">
            <template #body="slotProps">
              {{
                slotProps.data.arabic_deg || slotProps.data.arabic_deg === 0
                  ? Math.abs(slotProps.data.arabic_deg)
                  : "-"
              }}
            </template>
          </Column>
          <Column field="name" :header="$t('firstLanguage')">
            <template #body="slotProps">
              {{
                slotProps.data.first_lang_name &&
                !(student.lang_1 === 6) &&
                (slotProps.data.lang_1_deg || slotProps.data.lang_1_deg === 0)
                  ? Math.abs(slotProps.data.lang_1_deg)
                  : "-"
              }}
            </template>
          </Column>
          <Column field="name" :header="$t('secondLanguage')">
            <template #body="slotProps">
              {{
                slotProps.data.second_lang_name &&
                !(student.lang_2 === 6) &&
                (slotProps.data.lang_2_deg || slotProps.data.lang_2_deg === 0)
                  ? Math.abs(slotProps.data.lang_2_deg)
                  : "-"
              }}
            </template>
          </Column>
          <Column
            field="name"
            :header="$t('pureMath')"
            v-if="scientificMathBranch === true"
          >
            <template #body="slotProps">
              {{
                slotProps.data.pure_math_deg ||
                slotProps.data.pure_math_deg === 0
                  ? Math.abs(slotProps.data.pure_math_deg)
                  : "-"
              }}
            </template>
          </Column>
          <Column field="name" :header="$t('history')" v-if="literar === true">
            <template #body="slotProps">
              {{
                slotProps.data.history_deg || slotProps.data.history_deg === 0
                  ? Math.abs(slotProps.data.history_deg)
                  : "-"
              }}
            </template>
          </Column>
          <Column
            field="name"
            :header="$t('geography')"
            v-if="literar === true"
          >
            <template #body="slotProps">
              {{
                slotProps.data.geography_deg ||
                slotProps.data.geography_deg === 0
                  ? Math.abs(slotProps.data.geography_deg)
                  : "-"
              }}
            </template>
          </Column>
          <Column
            field="name"
            :header="$t('philosophy')"
            v-if="literar === true"
          >
            <template #body="slotProps">
              {{
                slotProps.data.philosophy_deg ||
                slotProps.data.philosophy_deg === 0
                  ? Math.abs(slotProps.data.philosophy_deg)
                  : "-"
              }}
            </template>
          </Column>
          <Column
            field="name"
            :header="$t('psychology')"
            v-if="literar === true"
          >
            <template #body="slotProps">
              {{
                slotProps.data.psychology_deg ||
                slotProps.data.psychology_deg === 0
                  ? Math.abs(slotProps.data.psychology_deg)
                  : "-"
              }}
            </template>
          </Column>
          <Column
            field="name"
            :header="$t('chemistry')"
            v-if="
              scientificMathBranch === true || scientificScienceBranch === true
            "
          >
            <template #body="slotProps">
              {{
                slotProps.data.chemistry_deg ||
                slotProps.data.chemistry_deg === 0
                  ? Math.abs(slotProps.data.chemistry_deg)
                  : "-"
              }}
            </template>
          </Column>
          <Column
            field="name"
            :header="$t('biology')"
            v-if="scientificScienceBranch === true"
          >
            <template #body="slotProps">
              {{
                slotProps.data.biology_deg || slotProps.data.biology_deg === 0
                  ? Math.abs(slotProps.data.biology_deg)
                  : "-"
              }}
            </template>
          </Column>
          <Column
            field="name"
            :header="$t('geology')"
            v-if="scientificScienceBranch === true"
          >
            <template #body="slotProps">
              {{
                slotProps.data.geology_deg || slotProps.data.geology_deg === 0
                  ? Math.abs(slotProps.data.geology_deg)
                  : "-"
              }}
            </template>
          </Column>
          <Column
            field="name"
            :header="$t('appliedMath')"
            v-if="scientificMathBranch === true"
          >
            <template #body="slotProps">
              {{
                slotProps.data.applied_math_deg ||
                slotProps.data.applied_math_deg === 0
                  ? Math.abs(slotProps.data.applied_math_deg)
                  : "-"
              }}
            </template>
          </Column>
          <Column
            field="name"
            :header="$t('physics')"
            v-if="
              scientificMathBranch === true || scientificScienceBranch === true
            "
          >
            <template #body="slotProps">
              {{
                slotProps.data.physics_deg || slotProps.data.physics_deg === 0
                  ? Math.abs(slotProps.data.physics_deg)
                  : "-"
              }}
            </template>
          </Column>
          <Column field="name" :header="$t('totalGrade')">
            <template #body="slotProps">
              {{
                slotProps.data.total_degree || slotProps.data.total_degree === 0
                  ? Math.abs(slotProps.data.total_degree)
                  : "-"
              }}
            </template></Column
          >
          <Column field="name" :header="$t('religiousEducation')">
            <template #body="slotProps">
              {{
                slotProps.data.religious_education_deg ||
                slotProps.data.religious_education_deg === 0
                  ? Math.abs(slotProps.data.religious_education_deg)
                  : "-"
              }}
            </template>
          </Column>
          <Column field="name" :header="$t('nationalEducation')">
            <template #body="slotProps">
              {{
                slotProps.data.national_education_deg ||
                slotProps.data.national_education_deg === 0
                  ? Math.abs(slotProps.data.national_education_deg)
                  : "-"
              }}
            </template></Column
          >
          <Column field="name" :header="$t('economics')">
            <template #body="slotProps">
              {{
                slotProps.data.economics_deg ||
                slotProps.data.economics_deg === 0
                  ? Math.abs(slotProps.data.economics_deg)
                  : "-"
              }}
            </template>
          </Column>
          <Column field="name" :header="$t('noOfFail')">
            <template #body="slotProps">
              {{
                slotProps.data.no_of_fail || slotProps.data.no_of_fail === 0
                  ? Math.abs(slotProps.data.no_of_fail)
                  : "-"
              }}
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
  </template>
</template>

<script setup lang="ts">
import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import { InquireCDStudentProvider } from "@/providers/inquireCDStudent";
import { onMounted, ref, type Ref } from "vue";
import LabeledValue from "../shared/basic/LabeledValue.vue";
import { ApplicationEnum, RightsEnum } from "@/utils/enums";
import PageLoader from "../shared/basic/PageLoader.vue";
import type { CDStudent } from "@/utils/types";

// Static Variables
const app = ApplicationEnum.INQUIRE_CD_STUDENT;

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");

// Student Data
const student: Ref<CDStudent> = ref({});
const scientificMathBranch: Ref<boolean> = ref(false);
const scientificScienceBranch: Ref<boolean> = ref(false);
const literar: Ref<boolean> = ref(false);

// Define Component Inputs (Props)
const props = defineProps({
  selectedYear: { type: String, default: "2021" },
  nationalId: { type: String, default: "" },
  seatNumber: { type: Number, default: 0 },
});

// Define Component Outputs (Emits)
const emit = defineEmits(["edit", "delete"]);

onMounted(async () => {
  if (props.nationalId || props.seatNumber) {
    await getStudentData(
      props.selectedYear,
      props.nationalId,
      props.seatNumber
    );
  }
});

const getStudentData = async (
  selectedYear: string,
  nationalId: string,
  seatNumber: number
) => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    await InquireCDStudentProvider.getStudent(
      selectedYear,
      nationalId,
      seatNumber
    ).then((data) => {
      student.value = data.payload.student;
      student.value.date_of_birth =
        student.value.day +
        "-" +
        student.value.month +
        "-" +
        student.value.year;
    });
    scientificMathBranch.value = false;
    scientificScienceBranch.value = false;
    literar.value = false;
    if (student.value.branch_code_new === 1) {
      scientificScienceBranch.value = true;
    } else if (student.value.branch_code_new === 2) {
      scientificMathBranch.value = true;
    } else if (student.value.branch_code_new === 5) {
      literar.value = true;
    } else {
      scientificMathBranch.value = true;
      scientificScienceBranch.value = true;
      literar.value = true;
    }
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const editStudent = () => {
  emit("edit", student.value);
};

const deleteStudent = () => {
  emit("delete", student.value);
};
</script>

<style scoped lang="scss">
.view-container {
  display: grid;
  grid-template-columns: 1fr;
}
.table-container {
  min-width: 100%;
}
.table-container {
  overflow-x: auto;
  border-inline-start: 2px solid var(--primary-color);
  background-color: var(--surface-50);
}
.menu-opened .table-container {
  max-width: none;
}
.menu-closed .table-container {
  max-width: none;
}
@media screen and (min-width: 768px) {
  .view-container {
    grid-template-columns: 1fr 1fr;
  }
  .menu-opened .table-container {
    max-width: 68vw;
  }
  .menu-closed .table-container {
    max-width: 91vw;
  }
}
@media screen and (min-width: 992px) {
  .view-container {
    grid-template-columns: 1fr 1fr 1fr;
  }
}
@media screen and (min-width: 1150px) {
  .menu-opened .table-container {
    max-width: 72vw;
  }
}
</style>
