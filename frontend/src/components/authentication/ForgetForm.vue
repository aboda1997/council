<template>
  <div class="container flex align-items-center justify-content-center">
    <div class="p-card forget-card w-full md:w-6 lg:w-5 xl:w-4">
      <div class="flex flex-row align-items-center justify-content-center mb-4">
        <i class="pi pi-envelope forget-logo"></i>
        <h3 class="my-0 mx-2">{{ $t("resetPassword") }}</h3>
      </div>
      <form @submit="submitResetPasswordForm">
        <div>
          <div class="field col-12 mb-2">
            <span class="p-float-label">
              <InputText
                id="email"
                type="email"
                class="w-full"
                v-model="userEmail"
              />
              <label for="email">{{ $t("emailInput") }}</label>
            </span>
            <small
              v-for="error of v$.userEmail.$errors"
              :key="error.$uid"
              class="p-error"
            >
              {{ error.$message }}
            </small>
          </div>

          <div class="flex justify-content-end px-2 mb-3">
            <a
              class="font-medium no-underline text-primary text-right cursor-pointer"
              @click="navigateToLogin"
              >{{ $t("loginInLink") }}</a
            >
          </div>
          <div class="flex flex-row">
            <Button
              :label="$t('send')"
              icon="pi pi-sign-in icon-fix"
              class="forget-btn flex-1 mx-2"
              :loading="isLoading"
              @click="submitResetPasswordForm"
            >
            </Button>
            <LangSwitcher
              class="forget-btn mx-2 px-2 forget-lang-switcher"
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
import {
  showToastMessage,
  showErrorToastMessage,
  clearToastMessages,
} from "@/utils/globals";
import { useI18n } from "vue-i18n";
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useVuelidate } from "@vuelidate/core";
import {
  required,
  email,
  createI18nMessage,
  type MessageProps,
} from "@vuelidate/validators";

// Importing Services
const { t } = useI18n();
const router = useRouter();

// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `forgetPasswordValidations.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

// UI states
const isLoading = ref(false);

// Form Fields
const userEmail = ref("");

// Form Validation Rules
const rules = computed(() => ({
  userEmail: {
    requiredEmail: withI18nMessage(required),
    emailType: withI18nMessage(email),
  },
}));
const v$ = useVuelidate(rules, { userEmail });

// Component Functions
const navigateToLogin = () => {
  router.push("/login");
};

const submitResetPasswordForm = async () => {
  const lang = localStorage.getItem("lang");
  isLoading.value = true;
  const isFormValid = await v$.value.$validate();
  if (isFormValid) {
    clearToastMessages();
    try {
      const result = await AuthenticationProvider.submitEmail(
        userEmail.value,
        lang
      );
      router.push("/confirmEmailMessage");
      showToastMessage(result.detail);
    } catch (error) {
      showErrorToastMessage(error);
    }
  }
  isLoading.value = false;
};
</script>

<style scoped lang="scss">
.forget-logo {
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
.forget-card {
  padding: 32px;
}
.forget-btn {
  height: 47px;
  line-height: 1;
}
@media (max-width: 300px) {
  .lang-ar .forget-btn {
    font-size: 0.85rem;
  }
}
.forget-lang-switcher {
  border-radius: 6px;
}
</style>
