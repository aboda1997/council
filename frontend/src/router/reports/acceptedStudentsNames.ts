import type { RouteRecordRaw } from "vue-router";
import { ApplicationEnum } from "@/utils/enums";
import numberAcceptedStudentsVue from "@/components/reports/acceptedStudentsNames/acceptedStudentsNames.vue";

// All routes related to number Accepted Students report should be here,
export const acceptedStudentsNamesRoutes: RouteRecordRaw[] = [
  {
    path: "/acceptedStudentsNames",
    name: "acceptedStudentsNames",
    component: numberAcceptedStudentsVue,
    meta: {
      application: ApplicationEnum.ACCEPTED_STUDENT_NAMES,
    },
  },
];
