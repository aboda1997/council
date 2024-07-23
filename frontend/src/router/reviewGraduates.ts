import type { RouteRecordRaw } from "vue-router";
import { ApplicationEnum } from "@/utils/enums";
import ReviewGraduatesVue from "@/components/reviewGraduates/reviewGraduates.vue";

// All routes related to upload student CD File Applcation should be here,
export const reviewGraduatesRoutes: RouteRecordRaw[] = [
  {
    path: "/reviewGraduates",
    name: "reviewGraduates",
    component: ReviewGraduatesVue,
    meta: {
      application: ApplicationEnum.REVIEW_GRADUATES,
    },
  },
];
