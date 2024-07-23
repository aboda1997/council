import type { RouteRecordRaw } from "vue-router";
import { ApplicationEnum } from "@/utils/enums";
import inquireGraduateInfoVue from "@/components/inquireGraduateInfo/inquireGraduateInfo.vue";

// All routes related to inquire Student Info application should be here,
export const inquireGraduateInfoRoutes: RouteRecordRaw[] = [
  {
    path: "/inquireGraduateInfo",
    name: "inquireGraduateInfo",
    component: inquireGraduateInfoVue,
    meta: {
      application: ApplicationEnum.GRADUATE_INFO,
    },
  },
];
