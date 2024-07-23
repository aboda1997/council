import type { RouteRecordRaw } from "vue-router";
import { ApplicationEnum } from "@/utils/enums";
import inquireStudentInfoVue from "@/components/inquireStudentInfo/inquireStudentInfo.vue";

// All routes related to inquire Student Info application should be here,
export const inquireStudentInfoRoutes: RouteRecordRaw[] = [
  {
    path: "/inquireStudentInfo",
    name: "inquireStudentInfo",
    component: inquireStudentInfoVue,
    meta: {
      application: ApplicationEnum.STUDENT_INFO,
    },
  },
];
