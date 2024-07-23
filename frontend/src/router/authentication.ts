import LoginVue from "@/components/authentication/LoginForm.vue";
import ForgetVue from "@/components/authentication/ForgetForm.vue";
import ResetVue from "@/components/authentication/ResetForm.vue";
import EmailConfirm from "@/components/authentication/EmailConfirm.vue";
import invalidToken from "@/components/authentication/InvalidToken.vue";
import type { RouteRecordRaw } from "vue-router";

// All routes related to user authentication should be here,
// such login, forget my password etc...
export const authenticationRoutes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "login",
    component: LoginVue,
    meta: {
      publicRoute: true,
    },
  },
  {
    path: "/forget",
    name: "forget",
    component: ForgetVue,
    meta: {
      publicRoute: true,
    },
  },
  {
    path: "/forgotmypassword",
    name: "forgetTest",
    component: ForgetVue,
    meta: {
      publicRoute: true,
    },
  },
  {
    path: "/resetmypassword",
    name: "ResetVue",
    component: ResetVue,
    meta: {
      publicRoute: true,
    },
  },
  {
    path: "/confirmEmailMessage",
    name: "EmailConfirm",
    component: EmailConfirm,
    meta: {
      publicRoute: true,
    },
  },
  {
    path: "/invalidtoken",
    name: "invalidToken",
    component: invalidToken,
    meta: {
      publicRoute: true,
    },
  },
];
