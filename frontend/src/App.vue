<script setup lang="ts">
import { RouterView } from "vue-router";
import GlobalLayout from "./components/layouts/GlobalLayout.vue";
</script>

<template>
  <GlobalLayout>
    <RouterView />
  </GlobalLayout>
</template>

<style lang="scss">
@import "@/assets/scss/main.scss";
</style>
