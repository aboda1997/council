<template>
  <div class="labeled-value">
    <p class="label">{{ $t(props.label) }}:</p>
    <p class="value" v-if="props.serverTranslate">
      {{
        props.value
          ? $serverTranslate(props.value.toString())
          : $t(props.noDataLabel)
      }}
    </p>
    <p class="value" v-else>
      {{ props.value ? props.value : $t(props.noDataLabel) }}
    </p>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  label: { type: String, default: "" },
  value: { type: [String, Number], default: "" },
  serverTranslate: { type: Boolean, default: false },
  noDataLabel: { type: String, default: "‎" },
});
</script>

<style scoped lang="scss">
.labeled-value {
  margin: 0.5rem;
  border-inline-start: 2px solid var(--primary-color);
  background-color: var(--surface-50);
  border-radius: 0.35rem;
  padding: 0.5rem;
  @media screen and (max-width: 768px) {
    margin: 0.5rem 0;
  }
  p {
    margin: 0px;
    line-height: 1.25rem;
  }
  p.label {
    font-weight: bold;
    font-size: 0.875rem;
  }
  p.value {
    font-size: 0.9rem;
    overflow-wrap: anywhere;
    white-space: pre-wrap;
  }
}
</style>
