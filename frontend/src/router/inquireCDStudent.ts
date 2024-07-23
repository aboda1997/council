import type { RouteRecordRaw } from "vue-router";
import { ApplicationEnum } from "@/utils/enums";
import inquireCDStudentVue from "@/components/inquireCDStudent/inquireCDStudent.vue";

// All routes related to inquire Student Info application should be here,
export const inquireCDStudentRoutes: RouteRecordRaw[] = [
  {
    path: "/inquireCDStudent",
    name: "inquireCDStudent",
    component: inquireCDStudentVue,
    meta: {
      application: ApplicationEnum.INQUIRE_CD_STUDENT,
    },
  },
];
