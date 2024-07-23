<template>
  <div class="container flex align-items-center justify-content-center">
    <div class="p-card reset-card w-full md:w-6 lg:w-5 xl:w-4">
      <div class="flex flex-row align-items-center justify-content-center mb-4">
        <i class="pi pi-user reset-logo"></i>
        <h3 class="my-0 mx-2">{{ $t("resetPassword") }}</h3>
      </div>
      <form @submit="submitResetPasswordForm">
        <div>
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
          <div class="field col-12 mb-0">
            <span class="p-float-label">
              <InputText
                id="password"
                type="password"
                class="w-full"
                v-model="rePassword"
              />
              <label for="rePassword">{{ $t("confirmPasswordInput") }}</label>
            </span>
            <small
              v-for="error of v$.rePassword.$errors"
              :key="error.$uid"
              class="p-error"
            >
              {{ error.$message }}
              <br />
            </small>
          </div>

          <div class="flex flex-row">
            <Button
              :label="$t('save')"
              icon="pi pi-sign-in icon-fix"
              class="reset-btn flex-1 mx-2"
              :loading="isLoading"
              @click="submitResetPasswordForm"
            >
            </Button>
            <LangSwitcher
              class="reset-btn mx-2 px-2 reset-lang-switcher"
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
import { ref, computed, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useVuelidate } from "@vuelidate/core";
import {
  maxLength,
  minLength,
  required,
  sameAs,
  createI18nMessage,
  type MessageProps,
} from "@vuelidate/validators";

// Importing Services
const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const emailToken = route.query.token;
// Importing i18n Message Localization for the validators
const messagePath = ({ $validator }: MessageProps): string =>
  `forgetPasswordValidations.${$validator}`;
const withI18nMessage = createI18nMessage({ t, messagePath });

// UI states
const isLoading = ref(false);

// Form Fields
const password = ref("");
const rePassword = ref("");
// Form Validation Rules
const rules = computed(() => ({
  password: {
    requiredPassword: withI18nMessage(required),
    maxLengthPassword: withI18nMessage(maxLength(50)),
    minLengthPassword: withI18nMessage(minLength(8)),
  },
  rePassword: {
    requiredPassword: withI18nMessage(required),
    maxLengthPassword: withI18nMessage(maxLength(50)),
    minLengthPassword: withI18nMessage(minLength(8)),
    sameAsPass: withI18nMessage(sameAs(password)),
  },
}));
const v$ = useVuelidate(rules, { password, rePassword });

onMounted(async () => {
  try {
    const result = await AuthenticationProvider.checkToken(emailToken);
    console.log(result);
  } catch (error) {
    console.log(error);
    router.push("/invalidtoken");
  }
});

const submitResetPasswordForm = async () => {
  isLoading.value = true;
  const isFormValid = await v$.value.$validate();
  if (isFormValid) {
    clearToastMessages();
    try {
      const result = await AuthenticationProvider.saveNewPassword(
        password.value,
        rePassword.value,
        emailToken
      );

      router.push("/login");
      showToastMessage(result.detail);
    } catch (error) {
      showErrorToastMessage(error);
    }
  }
  isLoading.value = false;
};
</script>

<style scoped lang="scss">
.reset-logo {
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
.reset-card {
  padding: 32px;
}
.reset-btn {
  height: 47px;
  line-height: 1;
}
.p-inputtext {
  margin: 6px;
}
@media (max-width: 300px) {
  .lang-ar .reset-btn {
    font-size: 0.85rem;
  }
}
.reset-lang-switcher {
  border-radius: 6px;
}
</style>
