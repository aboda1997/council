<!-- TODO: replace this test structure with actual main structure -->
<template>
  <div class="main-wrapper">
    <AppTopBar @menu-toggle-event="toggleMenu" />
    <div class="sidebar-wrapper" :class="menuCssClass">
      <AppSidebar :menuOpen="menuOpen" />
      <div class="content-wrapper">
        <AppBreadCrumps />
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppTopBar from "../shared/AppTopBar.vue";
import AppSidebar from "../shared/AppSidebar.vue";
import AppBreadCrumps from "../shared/AppBreadCrumps.vue";
import { computed, ref } from "vue";

const menuOpen = ref(true);
const menuCssClass = computed(() => {
  return menuOpen.value ? "menu-opened" : "menu-closed";
});

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value;
};
</script>

<style scoped lang="scss">
.main-wrapper {
  background: var(--layout-background-color);
  display: flex;
  flex-direction: column;
  height: inherit;
}
.sidebar-wrapper {
  flex-grow: 1;
  display: flex;
  flex-direction: row;
  height: calc(100% - 3rem);
  max-width: 100vw;
}
.content-wrapper {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  max-width: 100vw;
}
</style>
