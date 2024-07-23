import type { RouteRecordRaw } from "vue-router";
import { ApplicationEnum } from "@/utils/enums";
import militaryEducationVue from "@/components/militaryEducation/militaryEducation.vue";

// All routes related to inquire Student Info application should be here,
export const militaryEducationRoutes: RouteRecordRaw[] = [
  {
    path: "/militaryEducation",
    name: "militaryEducation",
    component: militaryEducationVue,
    meta: {
      application: ApplicationEnum.MILITARY_EDUCATION,
    },
  },
];
