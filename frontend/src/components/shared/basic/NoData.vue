<template>
  <div
    class="flex flex-column align-items-center justify-content-center flex-grow-1 no-data-wrapper"
  >
    <div class="flex flex-row align-items-center justify-content-center">
      <i
        v-if="props.icon"
        class="pi no-data-logo icon-fix"
        :class="props.icon"
      ></i>
      <h3 v-if="props.text" class="no-data-text my-0 mx-2">
        {{ $t(props.text) }}
      </h3>
    </div>
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  text: { type: String, default: "noDisplayData" },
  icon: { type: String, default: "pi-ban" },
});
</script>

<style lang="scss" scoped>
.no-data-wrapper {
  background-color: #e9ecefc0;
  border-radius: 1rem;
  margin: 1.5rem 0.75rem;
  .no-data-logo {
    color: var(--secondary-color);
    opacity: 0.85;
    font-size: 2.25rem;
  }
  .no-data-text {
    color: var(--secondary-color);
    opacity: 0.85;
    line-height: 1.15;
  }
  .no-data-text-small {
    font-size: 1rem;
  }
}
</style>
