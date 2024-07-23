import type {
  AppCategory,
  LoginResponse,
  UserApplication,
  UserModel,
  UserPermissions,
} from "@/utils/types";
import { useLocalStorage } from "@vueuse/core";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

// Store made to hand holding general user Data.
export const useUserDataStore = defineStore("userData", () => {
  // Empty User const
  const defaultUserData: UserModel = {};
  const defaultAppCategories: AppCategory[] = [];
  const defaultUserApplications: UserApplication[] = [];

  // Data Variables in the Store
  const accessToken = ref(useLocalStorage("accessToken", ""));
  const userData = ref(useLocalStorage("userData", defaultUserData));
  const appCategories = ref(
    useLocalStorage("appCategories", defaultAppCategories)
  );
  const userApplications = ref(
    useLocalStorage("userApplications", defaultUserApplications)
  );

  // Computed Variables in the Store
  const isAuthenticated = computed(() =>
    accessToken.value !== "" ? true : false
  );

  // Functions running on Variables in the Store.
  const saveUserData = (data: LoginResponse) => {
    accessToken.value = data.payload.accessToken;
    userData.value = data.payload.userData;
    updateUserPermissions(data.payload.userPermissions);
  };

  const updateUserPermissions = (data: UserPermissions) => {
    appCategories.value = data.appCategories;
    userApplications.value = data.userApplications;
  };

  const resetUserData = () => {
    accessToken.value = "";
    userData.value = defaultUserData;
    appCategories.value = defaultAppCategories;
    userApplications.value = defaultUserApplications;
  };

  return {
    accessToken,
    userData,
    isAuthenticated,
    appCategories,
    userApplications,
    saveUserData,
    resetUserData,
    updateUserPermissions,
  };
});
