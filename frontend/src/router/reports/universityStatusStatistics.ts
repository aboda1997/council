import type { RouteRecordRaw } from "vue-router";
import { ApplicationEnum } from "@/utils/enums";
import universityStatusStatisticsVue from "@/components/reports/universityStatusStatistics/universityStatusStatistics.vue";

// All routes related to number Accepted Students report should be here,
export const universityStatusStatisticsRoutes: RouteRecordRaw[] = [
  {
    path: "/universityStatusStatistics",
    name: "universityStatusStatistics",
    component: universityStatusStatisticsVue,
    meta: {
      application: ApplicationEnum.UNIVERSITY_STATUS_STATISTICS,
    },
  },
];
