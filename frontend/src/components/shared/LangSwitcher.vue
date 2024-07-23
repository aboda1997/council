<template>
  <Button
    v-tooltip.bottom="{ value: $t('changeLang') }"
    class="lang-switcher p-button-outlined"
    :loading="isLoading"
    @click="switchLang()"
  >
    <div class="flex align-items-baseline">
      <i class="pi pi-globe"></i>
      <span class="font-xsmall">{{ $t("switchToLang") }}</span>
    </div>
  </Button>
</template>

<script setup lang="ts">
import { useLangStore } from "@/stores/language";
import { ref } from "vue";
import Button from "primevue/button";

const langStore = useLangStore();
let isLoading = ref(false);

const switchLang = () => {
  isLoading.value = true;
  langStore.changeLang();
  isLoading.value = false;
};
</script>

<style scoped lang="scss">
.p-button.p-button-outlined.lang-switcher {
  direction: ltr;
  padding: 0.375rem;
  color: var(--secondary-color);
  border-color: var(--secondary-color);
  &:hover {
    color: var(--secondary-hover-color);
    border-color: var(--secondary-hover-color);
  }
}
.font-xsmall {
  font-weight: bold;
  font-size: 0.625rem;
}
</style>
