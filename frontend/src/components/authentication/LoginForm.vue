<template>
  <div class="container flex align-items-center justify-content-center">
    <div class="p-card login-card w-full md:w-6 lg:w-5 xl:w-4">
      <div class="flex flex-row align-items-center justify-content-center mb-4">
        <i class="pi pi-user login-logo"></i>
        <h3 class="my-0 mx-2">{{ $t("login") }}</h3>
      </div>
      <form @submit="submitLoginForm">
        <div>
          <div class="field col-12 mb-2">
            <span class="p-float-label">
              <InputText
                id="username"
                type="text"
                class="w-full"
                v-model="username"
              />
              <label for="username">{{ $t("userNameInput") }}</label>
            </span>
            <small
              v-for="error of v$.username.$errors"
              :key="error.$uid"
              class="p-error"
            >
              {{ error.$message }}
            </small>
          </div>

          <div class="field col-12 mb-0">
            <span class="p-float-label">
              <InputText
                id="password"
                type="password"
                class="w-full"
                v-model="password"
              />
              <label for="password">{{ $t("passwordInput") }}</label>
            </span>
            <small
              v-for="error of v$.password.$errors"
              :key="error.$uid"
              class="p-error"
            >
              {{ error.$message }}
              <br />
            </small>
          </div>

          <div class="flex justify-content-end px-2 mb-3">
            <a
              class="font-medium no-underline text-primary text-right cursor-pointer"
              @click="navigateToForgotPassword"
              >{{ $t("forgotPasswordLink") }}</a
            >
          </div>
          <div class="flex flex-row">
            <Button
              :label="$t('login')"
              icon="pi pi-sign-in icon-fix"
              class="login-btn flex-1 mx-2"
              :loading="isLoading"
              @click="submitLoginForm"
            >
            </Button>
            <LangSwitcher
              class="login-btn mx-2 px-2 login-lang-switcher"
            ></LangSwitcher>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import LangSwitcher from "@/components/shared/LangSwitcher.vue";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import { AuthenticationProvider } from "@/providers/authentication";
import { useUserDataStore } from "@/stores/userData";
import {
  showToastMessage,
  showErrorToastMessage,
  clearToastMessages,
} from "@/utils/globals";
import { useI18n } from "vue-i18n";
import { ref, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useVuelidate } from "@vuelidate/core";
import {
  maxLength,
  required,
  createI18nMessage,
  type MessageProps,
} from "@vuelidate/validators";

// Importing Services
const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const userDataStore = useUserDataStore();

// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `loginValidations.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

// UI states
const isLoading = ref(false);

// Form Fields
const username = ref("");
const password = ref("");

// Form Validation Rules
const rules = computed(() => ({
  username: {
    requiredUsername: withI18nMessage(required),
    maxLengthUsername: withI18nMessage(maxLength(50)),
  },
  password: {
    requiredPassword: withI18nMessage(required),
    maxLengthPassword: withI18nMessage(maxLength(50)),
  },
}));
const v$ = useVuelidate(rules, { username, password });

// Component Functions
const navigateToForgotPassword = () => {
  router.push("/forgotmypassword");
};

const submitLoginForm = async () => {
  isLoading.value = true;
  const isFormValid = await v$.value.$validate();
  if (isFormValid) {
    clearToastMessages();
    try {
      const result = await AuthenticationProvider.submitLogin(
        username.value,
        password.value
      );
      const { redirect, ...query } = route.query;
      router.push({
        path: redirect?.toString() || "/",
        query: query,
      });
      userDataStore.saveUserData(result);
      showToastMessage(result.detail);
    } catch (error) {
      showErrorToastMessage(error);
    }
  }
  isLoading.value = false;
};
</script>

<style scoped lang="scss">
.login-logo {
  border-radius: 6px;
  padding: 6px;
  font-size: 1.5rem;
  border: solid 2px;
}
.container {
  width: inherit;
  height: 100%;
  background: url("@/assets/svg/wave-background.svg") center center no-repeat;
  background-size: cover;
  overflow: auto;
}
.login-card {
  padding: 32px;
}
.login-btn {
  height: 47px;
  line-height: 1;
}
@media (max-width: 300px) {
  .lang-ar .login-btn {
    font-size: 0.85rem;
  }
}
.login-lang-switcher {
  border-radius: 6px;
}
</style>
