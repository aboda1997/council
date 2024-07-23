<template>
  <slot></slot>
  <Toast :class="componentCSS" :position="toastPosition" group="global" />
  <ConfirmDialog :class="['global-dialog', componentCSS]"></ConfirmDialog>
</template>

<script setup lang="ts">
import Toast from "primevue/toast";
import ConfirmDialog from "primevue/confirmdialog";
import { usePrimeVue } from "primevue/config";
import { useLangStore } from "@/stores/language";
import { Language } from "@/utils/enums";
import { computed, onMounted, watch } from "vue";
import { useUserDataStore } from "@/stores/userData";
import { AuthenticationProvider } from "@/providers/authentication";
import { clearToastMessages, redirectToLogin } from "@/utils/globals";
import { primevueArLocale, primevueEnLocale } from "@/assets/i18n/primevue";

// Importing Services
const langStore = useLangStore();
const userDataStore = useUserDataStore();
const primevue = usePrimeVue();

// UI states
const toastPosition = computed(() =>
  langStore.locale === Language.ARABIC ? "bottom-right" : "bottom-left"
);
const componentCSS = computed(() =>
  langStore.locale === Language.ARABIC ? "p-component-ar" : "p-component-en"
);

watch(
  () => [langStore.locale],
  () => updatePrimeVueTranslation()
);

// Mounted Behaviour
onMounted(() => {
  getUserPermissions();
  document.body.classList.add(
    langStore.locale === Language.ARABIC ? "lang-ar" : "lang-en"
  );
  updatePrimeVueTranslation();
});

// Component Functions
const getUserPermissions = async () => {
  if (userDataStore.isAuthenticated) {
    clearToastMessages();
    try {
      const result = await AuthenticationProvider.getUserPermissions();
      userDataStore.updateUserPermissions(result.payload.userPermissions);
    } catch (error) {
      redirectToLogin();
    }
  }
};

const updatePrimeVueTranslation = () => {
  if (primevue && primevue.config) {
    primevue.config.locale =
      langStore.locale === Language.ARABIC
        ? primevueArLocale
        : primevueEnLocale;
  }
};
</script>

<style scoped></style>
