import NotFoundVue from "@/components/shared/NotFound.vue";

import NotAllowedVue from "@/components/shared/NotAllowed.vue";
import { useUserDataStore } from "@/stores/userData";
import type { ApplicationEnum } from "@/utils/enums";
import { hasPermission } from "@/utils/filters";
import {
  createRouter,
  createWebHistory,
  type RouteLocationNormalized,
  type RouteRecordRaw,
} from "vue-router";
import { authenticationRoutes } from "./authentication";
import { inquireCDStudentRoutes } from "./inquireCDStudent";
import { inquireStudentInfoRoutes } from "./inquireStudentInfo";
import { uploadCDFileRoutes } from "./uploadCDFile";
import { militaryEducationRoutes } from "./militaryEducation";
import { reviewGraduatesRoutes } from "./reviewGraduates";
import { inquireGraduateInfoRoutes } from "./inquireGraduateInfo";
import { transferStudentsRoutes } from "./transferStudents";
import { numberAcceptedStudentsRoutes } from "./reports/numberAcceptedStudents";
import { acceptedStudentsNamesRoutes } from "./reports/acceptedStudentsNames";
import { reviewInitiallyAcceptedRoutes } from "./reviewInitiallyAccepted";
import { universityStatusStatisticsRoutes } from "./reports/universityStatusStatistics";

// Application Base Routes
const baseRoutes: RouteRecordRaw[] = [
  {
    path: "/notFound",
    name: "notFound",
    component: NotFoundVue,
    meta: {
      publicRoute: true,
    },
  },
  {
    path: "/notAllowed",
    name: "notAllowed",
    component: NotAllowedVue,
    meta: {
      publicRoute: true,
    },
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "notFound",
  },
];

const applicationRoutes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "mainLayout",
    component: () => import("../components/layouts/MainLayout.vue"),
    children: [
      ...uploadCDFileRoutes,
      ...inquireCDStudentRoutes,
      ...inquireStudentInfoRoutes,
      ...militaryEducationRoutes,
      ...reviewGraduatesRoutes,
      ...inquireGraduateInfoRoutes,
      ...transferStudentsRoutes,
      ...numberAcceptedStudentsRoutes,
      ...acceptedStudentsNamesRoutes,
      ...reviewInitiallyAcceptedRoutes,
      ...universityStatusStatisticsRoutes,
    ],
  },
];

// All the of Application routes, added/chained together with concatnation.
const routes: RouteRecordRaw[] = [
  ...baseRoutes,
  ...authenticationRoutes,
  ...applicationRoutes,
];

// Global Router Guards
const authenticationGuard = (to: RouteLocationNormalized) => {
  const userDataStore = useUserDataStore();
  if (to.matched.some((record) => !record.meta.publicRoute)) {
    if (userDataStore.isAuthenticated) {
      return true;
    }
    return false;
  }
  return true;
};

const permissionGuard = (to: RouteLocationNormalized) => {
  const userDataStore = useUserDataStore();
  const canAccess = to.matched.every((record) => {
    if (userDataStore.isAuthenticated && record.meta.application) {
      return hasPermission(record.meta.application as ApplicationEnum);
    }
    return true;
  });
  return canAccess;
};

const loginRenavigationGuard = (to: RouteLocationNormalized) => {
  const userDataStore = useUserDataStore();
  if (to.name === "login" && userDataStore.isAuthenticated) {
    return false;
  }
  return true;
};

// Creates Application Router
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// Configure Router Guards to work
router.beforeEach((to) => {
  const canAccess = authenticationGuard(to);
  if (!canAccess) return { path: "/login" };
  const canAccessLogin = loginRenavigationGuard(to);
  if (!canAccessLogin) return { path: "/" };
  const hasAccessPerm = permissionGuard(to);
  if (!hasAccessPerm) return { path: "/notAllowed" };
  return true;
});

export default router;
