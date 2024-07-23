import type { RouteRecordRaw } from "vue-router";
import { ApplicationEnum } from "@/utils/enums";
import numberAcceptedStudentsVue from "@/components/reports/numberAcceptedStudents/numberAcceptedStudents.vue";

// All routes related to number Accepted Students report should be here,
export const numberAcceptedStudentsRoutes: RouteRecordRaw[] = [
  {
    path: "/numberAcceptedStudents",
    name: "numberAcceptedStudents",
    component: numberAcceptedStudentsVue,
    meta: {
      application: ApplicationEnum.NUMBER_ACCEPTED_STUDENTS,
    },
  },
];
