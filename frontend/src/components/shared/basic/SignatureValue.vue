<template>
  <div
    class="labeled-value"
    v-if="props.signature && props.signature.signatureName"
  >
    <p>
      <span class="label">{{ $t("updatedBy") }}&nbsp;</span>
      <span class="value">
        {{
          props.signature && props.signature.signatureName
            ? $serverTranslate(props.signature.signatureName) + "&nbsp;"
            : ""
        }}
      </span>
      <span class="label">{{ $t("at").toLocaleLowerCase() }}&nbsp;</span>
      <span class="value">
        {{ $displayDateTime(props.signature.signatureDate || "") }}
      </span>
    </p>
  </div>
  <div v-else></div>
</template>

<script setup lang="ts">
const props = defineProps({
  signature: { type: Object },
});
</script>

<style scoped lang="scss">
.labeled-value {
  background: hsl(282, 84%, 97%);
  border-width: 0px;
  border-inline-start: 2px solid var(--purple-500);
  border-inline-end: 2px solid var(--purple-500);
  border-radius: 0.35rem;
  margin: 0.5rem;
  padding: 0.5rem;
  @media screen and (max-width: 768px) {
    margin: 0.5rem 0;
  }
  p {
    margin: 0px;
    line-height: 1.25rem;
    font-size: 0.9rem;
  }
  .label {
    font-weight: normal;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }
  .value {
    font-weight: bold;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }
}
</style>
