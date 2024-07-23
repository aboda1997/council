import type { RouteRecordRaw } from "vue-router";
import { ApplicationEnum } from "@/utils/enums";
import transferStudentsVue from "@/components/transferStudents/transferStudents.vue";

// All routes related to inquire Student Info application should be here,
export const transferStudentsRoutes: RouteRecordRaw[] = [
  {
    path: "/transferStudents",
    name: "transferStudents",
    component: transferStudentsVue,
    meta: {
      application: ApplicationEnum.TRANSFER_STUDENTS,
    },
  },
];
