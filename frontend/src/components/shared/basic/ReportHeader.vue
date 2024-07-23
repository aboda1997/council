<template>
  <div class="report-header">
    <div class="header-div">
      <img
        class="report-coat-img"
        src="@/assets/svg/coat-of-arms-of-egypt.svg"
        alt="Egypt Coat of Arms"
      />
      <p>{{ $t("egyptName") }}</p>
      <p>{{ $t("highEducationMinistryName") }}</p>
      <p>{{ $t("pucName") }}</p>
    </div>
    <div class="header-div">
      <div class="title-wrapper">
        <h2>
          <template v-if="props.reportTitle">
            {{ $t(props.reportTitle || "") }}
          </template>
          <template v-else>
            {{ $serverTranslate(app?.displayName || "") }}
          </template>
        </h2>
        <p v-if="props.reportDetails">
          {{ $serverTranslate(props.reportDetails) }}
        </p>
      </div>
    </div>
    <div class="header-div">
      <p class="date-string">{{ dateString }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserDataStore } from "@/stores/userData";
import type { UserApplication } from "@/utils/types";
import { computed, onMounted, ref, type Ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

const { t } = useI18n();
const route = useRoute();
const userStore = useUserDataStore();

const app: Ref<UserApplication | undefined> = ref();
const currentDateTime: Ref<Date | undefined> = ref();

// Computed Variables
const dateString = computed(() => {
  if (currentDateTime.value) {
    const date = currentDateTime.value;
    const minutes = ("0" + date.getMinutes()).slice(-2);
    const hours = date.getHours();
    const hours12h = hours % 12 ? ("0" + (hours % 12)).slice(-2) : 12;
    const ampm = hours >= 12 ? "pm" : "am";
    const day = ("0" + date.getDate()).slice(-2);
    const month = ("0" + (date.getMonth() + 1)).slice(-2); //January is 0!
    const year = date.getFullYear();
    return (
      t("reportCreatedAt") +
      ": " +
      day +
      "-" +
      month +
      "-" +
      year +
      " | " +
      hours12h +
      ":" +
      minutes +
      " " +
      t(ampm)
    );
  }
  return "";
});

//
const props = defineProps({
  reportTitle: { type: String },
  reportDetails: { type: String },
});

onMounted(() => {
  currentDateTime.value = new Date(Date.now());
  if (!props.reportTitle) {
    updateCurrentApp();
  }
});

const updateCurrentApp = () => {
  const routeParts = route && route.path ? route.path.split("/") : [];
  if (routeParts.length > 1) {
    const appName = routeParts[1];
    app.value = userStore.userApplications.find((app) => app.name === appName);
  }
};
</script>

<style scoped lang="scss">
.report-header {
  line-height: 1.15;
  display: flex;
  justify-content: space-between;
  .header-div {
    margin: 4px 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-items: center;
    text-align: center;
    p {
      font-size: 10px;
      font-weight: bold;
      line-height: 1.15;
      margin: 0;
      &.date-string {
        font-size: 11px;
        margin: auto 0 0 0;
      }
    }
    .title-wrapper {
      margin: auto 0;
      h2 {
        font-size: 16px;
        margin: 0;
      }
    }
    .report-coat-img {
      max-width: 20px;
    }
  }
}
</style>
