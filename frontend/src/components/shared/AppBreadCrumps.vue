<template>
  <div
    v-if="route.path != '/'"
    class="p-breadcrumb p-component"
    aria-label="Breadcrumb"
  >
    <ul>
      <li class="p-breadcrumb-home pi pi-home"></li>
      <li
        class="p-breadcrumb-chevron pi pi-chevron-right"
        v-if="props.category || category"
      ></li>
      <li class="p-breadcrumb-text" v-if="props.category || category">
        {{
          $t(props.category || "") ||
          $serverTranslate(category?.displayName || "")
        }}
      </li>
      <li
        class="p-breadcrumb-chevron pi pi-chevron-right"
        v-if="props.app || app"
      ></li>
      <li class="p-breadcrumb-text" v-if="props.app || app">
        {{ $t(props.app || "") || $serverTranslate(app?.displayName || "") }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { onMounted, ref, watch, type Ref } from "vue";
import { useUserDataStore } from "@/stores/userData";
import type { AppCategory, UserApplication } from "@/utils/types";

const route = useRoute();
const userStore = useUserDataStore();
const app: Ref<UserApplication | undefined> = ref();
const category: Ref<AppCategory | undefined> = ref();
onMounted(() => {
  updateCurrentApp();
});
watch(
  () => [route.fullPath],
  () => updateCurrentApp()
);
const props = defineProps({
  app: { type: String },
  category: { type: String },
});

const updateCurrentApp = () => {
  const routeParts = route && route.path ? route.path.split("/") : [];
  if (routeParts.length > 1) {
    const appName = routeParts[1];
    app.value = userStore.userApplications.find((app) => app.name === appName);
    category.value = userStore.appCategories.find(
      (category) => category.id === app.value?.categoryId
    );
  }
};
</script>

<style lang="scss" scoped>
.p-breadcrumb {
  padding: 0.5rem;
  font-size: 0.85rem;
  line-height: 1.15;
  border-top: none;
  border-radius: 0;
  border-bottom-right-radius: 6px;
  border-bottom-left-radius: 6px;
  ul {
    display: flex;
    margin: 0;
    padding: 0;
    li {
      list-style: none;
    }
  }
  .p-breadcrumb-home {
    margin-top: -3px;
  }
  .p-breadcrumb-chevron {
    line-height: 1;
    font-size: 0.65rem;
  }
  .p-breadcrumb-text {
    margin-top: -3px;
  }
}
.page-title-container {
  background-color: var(--surface-a);
  padding: 4px;
}
.p-title-logo {
  border-radius: 6px;
  padding: 6px;
  font-size: 1.15rem;
  border: solid 2px;
}
.p-title-text {
  line-height: 1.15;
  font-weight: bold;
  font-size: 0.75rem;
}
</style>
