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
      ></div>
      <div>
        <h4 class="mt-2 mb-2 mx-2">
          {{ $t("studentData") }}
        </h4>
        <div class="view-container">
          <LabeledValue
            label="studentName"
            :value="student.studentName"
            :serverTranslate="true"
          />
          <LabeledValue
            v-if="
              !student.studentNationality_id ||
              student.studentNationality_id === 1
            "
            label="nationalID"
            :value="student.studentNID"
          />
          <LabeledValue
            v-if="
              student.studentNationality_id &&
              student.studentNationality_id !== 1
            "
            label="passport"
            :value="student.studentPassport"
          />
          <LabeledValue
            label="percentage"
            :value="studentUniversityEdu?.studentTot + '%' || ''"
          />
        </div>
      </div>
      <StudentUniversityDetails
        v-if="studentUniversityEdu"
        :showGraduationData="false"
        :studentUniversityEduData="studentUniversityEdu"
        :studentImposedCoursesData="studentImposedCourses"
      />
      <div>
        <h4 class="mt-2 mb-2 mx-2">
          {{ $t("attachments") }}
        </h4>
        <StudentFileUpload
          :allowUpload="$hasPermission(app, RightsEnum.EDIT)"
          :allowDelete="$hasPermission(app, RightsEnum.EDIT)"
          :provider="TransferStudentsProvider"
          :studentUniqueId="student.uniqueId"
          :attachments="studentAttachment"
          :maxAttachmentsCount="5"
          :maxAttachmentSize="2097152"
          :allowedMimetype="[
            'image/png',
            'image/jpg',
            'image/jpeg',
            'application/pdf',
          ]"
        />
      </div>
      <hr />
      <PageLoader
        v-if="isGettingFacultyData"
        :loading="isGettingFacultyData"
        error=""
      />
      <div v-else>
        <h4 class="mt-2 mb-2 mx-2">
          {{ $t("transferData") }}
        </h4>
        <div class="form-container">
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="studentUniveristy"
                class="w-full"
                :filter="true"
                :filterFields="['translatedName', 'name']"
                v-model="transferData.studentUniveristy_id"
                :options="translatedFormFilters.universities"
                :disabled="false"
                optionLabel="translatedName"
                optionValue="id"
                @change="filterFaculties()"
              />
              <label for="studentUniveristy"
                >{{ $t("transferUniversity") }}
              </label>
            </span>
          </div>
          <div class="field mt-3 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="studentFaculty"
                class="w-full"
                :filter="true"
                :filterFields="['translatedName', 'name']"
                v-model="transferData.studentFaculty_id"
                :options="filteredFaculties"
                :disabled="!transferData.studentUniveristy_id"
                optionLabel="translatedName"
                optionValue="id"
                @change="getFacultyReport()"
              />
              <label for="studentFaculty">{{ $t("transferFaculty") }} </label>
            </span>
          </div>
        </div>
        <div
          class="view-container"
          v-if="transferData.studentFaculty_id || showFacultyReport"
        >
          <LabeledValue
            label="allowedTransferCount"
            :value="facultyData.allowed_transfer_count || '0'"
          />
          <LabeledValue
            label="transferredStudentsCount"
            :value="facultyData.transferred_students_count || '0'"
          />
          <LabeledValue
            label="availableTransferPlaces"
            :value="facultyData.available_transfer_count || '0'"
          />
        </div>
        <div v-if="showFacultyReport && facultyData.can_transfer">
          <div class="form-container-3 mt-3 flex-grow-1">
            <div class="field mt-3 mx-2">
              <span class="p-float-label">
                <InputText
                  id="totalEquivHours"
                  class="w-full"
                  type="number"
                  v-model="totalEquivHours"
                />
                <label for="totalEquivHours">{{ $t("totalEquivHours") }}</label>
              </span>
              <small
                v-for="error of v$.transferData.totalEquivalentHours.$errors"
                :key="error.$uid"
                class="p-error"
              >
                {{ error.$message }} <br />
              </small>
            </div>
            <div class="field mt-3 mx-2">
              <span class="p-float-label">
                <Dropdown
                  id="studentLevel"
                  class="w-full"
                  :filter="true"
                  :filterFields="['translatedName', 'name']"
                  v-model="transferData.studentLevel_id"
                  :options="translatedFormFilters.levels"
                  optionLabel="translatedName"
                  optionValue="id"
                />
                <label for="studentLevel">{{ $t("transferLevel") }} </label>
              </span>
              <small
                v-for="error of v$.transferData.studentLevel_id.$errors"
                :key="error.$uid"
                class="p-error"
              >
                {{ error.$message }} <br />
              </small>
            </div>
            <div class="field mt-3 mx-2">
              <span class="p-float-label">
                <Calendar
                  id="transferDate"
                  class="w-full p-no-today"
                  panelClass="no-today-btn"
                  :showIcon="true"
                  :showButtonBar="true"
                  v-model="transferDate"
                  dateFormat="yy-mm-dd"
                />
                <label for="transferDate">{{ $t("transferDate") }} </label>
              </span>
            </div>
          </div>
          <div class="field mx-2">
            <div class="field-checkbox lg:m-0">
              <Checkbox
                id="fulfillmentToggle"
                v-model="isUnderFulfillment"
                :binary="true"
              />
              <label for="fulfillmentToggle"> {{ $t("notFulfilled") }} </label>
            </div>
          </div>
          <div class="field mt-5 mx-2">
            <span class="p-float-label">
              <Dropdown
                id="fulFillment"
                class="w-full"
                :filter="true"
                :filterFields="['translatedName', 'name']"
                v-model="transferData.transferFulfillment_id"
                :options="translatedFormFilters.fulfillments"
                :showClear="true"
                :disabled="!isUnderFulfillment"
                optionLabel="translatedName"
                optionValue="id"
              />
              <label for="fulFillment">{{ $t("fulFillmentReasons") }} </label>
            </span>
            <small
              v-for="error of v$.transferData.transferFulfillment_id.$errors"
              :key="error.$uid"
              class="p-error"
            >
              {{ error.$message }} <br />
            </small>
          </div>
        </div>
        <div
          class="header grid justify-content-end p-2 md:flex-row flex-column-reverse"
        >
          <div class="flex md:mt-2 align-items-center">
            <Button
              v-if="$hasPermission(app, RightsEnum.EDIT)"
              :label="$t('transferStudent')"
              class="save-button p-button p-button-primary p-button-sm flex-grow-1 mx-2 my-auto"
              @click="confirmTransferStudent()"
              :disabled="!facultyData.can_transfer"
            />
          </div>
        </div>
      </div>
    </div>
  </template>
</template>

<script setup lang="ts">
import Button from "primevue/button";
import Calendar from "primevue/calendar";
import Checkbox from "primevue/checkbox";
import Dropdown from "primevue/dropdown";
import InputText from "primevue/inputtext";
import {
  createI18nMessage,
  minValue,
  required,
  type MessageProps,
} from "@vuelidate/validators";
import useVuelidate from "@vuelidate/core";
import PageLoader from "../shared/basic/PageLoader.vue";
import LabeledValue from "../shared/basic/LabeledValue.vue";
import StudentUniversityDetails from "../shared/studentDetails/StudentUniversityDetails.vue";
import StudentFileUpload from "../shared/fileUpload/StudentFileUpload.vue";
import { computed, onMounted, ref, type Ref } from "vue";
import {
  ApplicationEnum,
  ConfirmDialogTypes,
  RightsEnum,
  ToastTypes,
} from "@/utils/enums";
import {
  showConfirmDialog,
  showErrorToastMessage,
  showToastMessage,
} from "@/utils/globals";
import type {
  Student,
  StudentImposedCourse,
  StudentSecondaryEdu,
  StudentUniversityEdu,
  TransferToFacultyReport,
  CouncilFilters,
  Faculty,
  UploadedFile,
} from "@/utils/types";
import { TransferStudentsProvider } from "@/providers/transferStudents";
import { serverTranslate } from "@/utils/filters";
import { useI18n } from "vue-i18n";
import { useGeneralStore } from "@/stores/general";

// Static Variables
const app = ApplicationEnum.TRANSFER_STUDENTS;

// Importing Services
const { t } = useI18n();
const generalStore = useGeneralStore();

// UI Variables
const isLoading: Ref<boolean> = ref(false);
const isGettingFacultyData: Ref<boolean> = ref(false);
const errorMessage: Ref<string> = ref("");
const showFacultyReport: Ref<boolean> = ref(false);

// Student Data
const student: Ref<Student> = ref({});
const studentSecondaryEdu: Ref<StudentSecondaryEdu | undefined> = ref();
const studentUniversityEdu: Ref<StudentUniversityEdu | undefined> = ref();
const studentImposedCourses: Ref<StudentImposedCourse[] | undefined> = ref();
const studentAttachment: Ref<UploadedFile[] | undefined> = ref();

const transferData: Ref<StudentUniversityEdu> = ref({});
const facultyData: Ref<TransferToFacultyReport> = ref({});

const filteredFaculties: Ref<Faculty[]> = ref([]);
const isUnderFulfillment: Ref<boolean> = ref(false);

// Form Filters
const formFilters: Ref<CouncilFilters> = ref({});

// Computed Values
const translatedFormFilters = computed(() => {
  return {
    universities: formFilters.value.universities?.map((university) => ({
      ...university,
      translatedName: university.name
        ? serverTranslate(university.name)
        : t("noData"),
    })),
    faculties: formFilters.value.faculties?.map((faculty) => ({
      ...faculty,
      translatedName: faculty.name
        ? serverTranslate(faculty.name)
        : t("noData"),
    })),
    levels: formFilters.value.levels?.map((level) => ({
      ...level,
      translatedName: level.name ? serverTranslate(level.name) : t("noData"),
    })),
    fulfillments: formFilters.value.fulfillments?.map((fulfillment) => ({
      ...fulfillment,
      translatedName: fulfillment.name
        ? serverTranslate(fulfillment.name)
        : t("noData"),
    })),
  };
});
const transferDate = computed({
  get(): Date | undefined {
    if (transferData.value.transferDate) {
      return new Date(transferData.value.transferDate);
    } else {
      return undefined;
    }
  },
  set(value: Date | undefined) {
    if (value) {
      const dd = String(value.getDate());
      const mm = String(value.getMonth() + 1); //January is 0!
      const yyyy = value.getFullYear();
      transferData.value.transferDate = yyyy + "-" + mm + "-" + dd;
    } else {
      transferData.value.transferDate = undefined;
    }
  },
});
const totalEquivHours = computed({
  get(): string | undefined {
    return transferData.value.totalEquivalentHours?.toString();
  },
  set(value: string | undefined) {
    transferData.value.totalEquivalentHours = value ? +value : undefined;
  },
});

// Define Component Inputs (Props)
const props = defineProps({
  studentId: { type: Number, default: 13 },
});

// Define Component Outputs (Emits)
const emit = defineEmits(["edit"]);

onMounted(async () => {
  if (props.studentId) {
    await getStudentData(props.studentId);
  }
});

const getStudentData = async (studentId: number) => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const result = await TransferStudentsProvider.getStudent(studentId);
    student.value = result.payload.student;
    studentSecondaryEdu.value = result.payload.studentSecondaryEdu;
    studentUniversityEdu.value = result.payload.studentUniversityEdu;
    studentImposedCourses.value = result.payload.studentImposedCourses;
    studentAttachment.value = result.payload.attachments;

    const filters = await TransferStudentsProvider.formFilters(
      studentUniversityEdu.value.studentFaculty_id,
      studentUniversityEdu.value.studentUniveristy_id
    );
    formFilters.value = filters.payload;

    const storedUnivId = generalStore.selectedTransferUniversity;
    if (
      formFilters.value.universities?.some((univ) => univ.id === storedUnivId)
    ) {
      transferData.value.studentUniveristy_id = storedUnivId;
      filterFaculties();
    }
  } catch (error) {
    errorMessage.value = error as string;
  }
  isLoading.value = false;
};

const filterFaculties = () => {
  generalStore.selectedTransferUniversity =
    transferData.value.studentUniveristy_id;

  transferData.value.studentFaculty_id = undefined;
  showFacultyReport.value = false;

  filteredFaculties.value = [];
  filteredFaculties.value =
    translatedFormFilters.value.faculties?.filter((faculty: Faculty) => {
      return faculty.univ === transferData.value.studentUniveristy_id;
    }) || [];
};

const getFacultyReport = async () => {
  if (transferData.value.studentFaculty_id) {
    isGettingFacultyData.value = true;
    errorMessage.value = "";
    try {
      const result = await TransferStudentsProvider.getFacultyData(
        transferData.value.studentFaculty_id
      );
      facultyData.value = result.payload;
      showFacultyReport.value = true;
    } catch (error) {
      showErrorToastMessage(error, ToastTypes.WARN);
    }
    isGettingFacultyData.value = false;
  }
};

const confirmTransferStudent = async () => {
  const isValid = await v$.value.$validate();
  if (isValid) {
    showConfirmDialog(
      t("transferStudentConfirmMessage"),
      (confirm: boolean) => {
        if (confirm) {
          transferStudent();
        }
      },
      ConfirmDialogTypes.CONFIRM
    );
  }
};

const transferStudent = async () => {
  if (student.value.id && transferData.value.studentFaculty_id) {
    isGettingFacultyData.value = true;
    errorMessage.value = "";
    try {
      if (!isUnderFulfillment.value) {
        transferData.value.transferFulfillment_id = undefined;
      }
      const result = await TransferStudentsProvider.transferStudent(
        student.value.id,
        transferData.value
      );
      showToastMessage(result.detail);
      resetValues();
      transferData.value.studentUniveristy_id = undefined;
      transferData.value.studentFaculty_id = undefined;
      await getStudentData(props.studentId);

      emit("edit", {
        student: student.value,
        studentUniversityEdu: studentUniversityEdu.value,
      });
    } catch (error) {
      showErrorToastMessage(error);
    }
    isGettingFacultyData.value = false;
  }
};

function resetValues() {
  facultyData.value = {};
  transferData.value = {};
  isUnderFulfillment.value = false;
  showFacultyReport.value = false;
  v$.value.transferData.$reset();
}

// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `transferStudentsValidations.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

const validateFulfillment = (value: number): boolean => {
  if (!isUnderFulfillment.value) {
    return true;
  }
  return value > 0;
};

const rules = {
  transferData: {
    totalEquivalentHours: {
      requiredTotalEquivHours: withI18nMessage(required),
      invalidTotalEquivHours: withI18nMessage(minValue(0)),
    },
    studentLevel_id: {
      requiredTransferLevel: withI18nMessage(required),
    },
    transferFulfillment_id: {
      requiredFulfillmentReason: withI18nMessage(validateFulfillment),
    },
  },
};

const v$ = useVuelidate(rules, { transferData });
</script>

<style scoped lang="scss">
.view-container {
  display: grid;
  grid-template-columns: 1fr;
}
@media screen and (min-width: 768px) {
  .view-container {
    grid-template-columns: 1fr 1fr;
  }
}
@media screen and (min-width: 992px) {
  .view-container {
    grid-template-columns: 1fr 1fr 1fr;
  }
}
.form-container {
  display: grid;
  grid-template-columns: 1fr;
}
@media screen and (min-width: 768px) {
  .form-container {
    grid-template-columns: 1fr 1fr;
  }
}

.form-container-3 {
  display: grid;
  grid-template-columns: 1fr;
}
@media screen and (min-width: 768px) {
  .form-container-3 {
    grid-template-columns: 1fr 1fr 1fr;
  }
}
</style>
