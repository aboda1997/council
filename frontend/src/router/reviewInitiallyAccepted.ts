import type { RouteRecordRaw } from "vue-router";
import { ApplicationEnum } from "@/utils/enums";
import ReviewInitiallyAcceptedVue from "@/components/reviewInitiallyAccepted/reviewInitiallyAccepted.vue";

// All routes related to upload student CD File Applcation should be here,
export const reviewInitiallyAcceptedRoutes: RouteRecordRaw[] = [
  {
    path: "/reviewInitiallyAccepted",
    name: "reviewInitiallyAccepted",
    component: ReviewInitiallyAcceptedVue,
    meta: {
      application: ApplicationEnum.REVIEW_INITIALLY_ACCEPTED,
    },
  },
];
