<template>
  <div v-if="props.loading" class="flex justify-content-center">
    <ProgressSpinner
      class="my-auto mx-3 p-page-loader"
      strokeWidth="8"
      animationDuration=".5s"
    />
    <h4 class="my-auto mx-0">{{ $t("loading") }}</h4>
  </div>
  <div v-else-if="props.error" class="flex align-items-center">
    <Message class="w-full" severity="error" :closable="false">
      {{ $serverTranslate(props.error) }}
    </Message>
  </div>
</template>

<script setup lang="ts">
import ProgressSpinner from "primevue/progressspinner";
import Message from "primevue/message";
const props = defineProps({
  loading: { type: Boolean, default: false },
  error: { type: String, default: "" },
});
</script>

<style scoped>
.p-page-loader {
  width: 50px;
  height: 50px;
}
</style>
