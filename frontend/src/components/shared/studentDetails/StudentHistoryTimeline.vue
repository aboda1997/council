<template>
  <Timeline
    :value="props.transactions"
    align="left"
    class="mt-3 customized-timeline"
  >
    <template #marker="slotProps">
      <span class="custom-marker shadow-2">
        <i :class="'pi pi-' + slotProps.item.icon.toString()"></i>
      </span>
    </template>
    <template #content="slotProps">
      <div class="labeled-value flex flex-column lg:flex-row">
        <div class="wrapper">
          <p class="title" v-if="slotProps.item.transactionType__name">
            <span class="value">
              {{
                slotProps.item.transactionType__name
                  ? $serverTranslate(slotProps.item.transactionType__name) +
                    "&nbsp;"
                  : ""
              }}
            </span>
          </p>
          <p
            class="changes"
            v-for="(change, index) of slotProps.item.transactionChanges"
            :key="index"
          >
            <span v-if="change.keyword" class="label">
              {{ $t(change.keyword || "") }}:
            </span>
            <span v-if="change.value" class="value">
              {{
                change.value
                  ? $serverTranslate(change.value.toString()) + "&nbsp;"
                  : ""
              }}
            </span>
            <span v-if="change.from" class="label"> {{ $t("before") }}: </span>
            <template v-if="change.from && Array.isArray(change.from)">
              <span
                class="value"
                v-for="(item, index) of change.from"
                :key="index"
              >
                {{ index !== 0 ? "," : "" }}
                {{ item ? $serverTranslate(item.toString()) + "&nbsp;" : "" }}
              </span>
            </template>
            <span v-else-if="change.from" class="value">
              {{
                change.from
                  ? $serverTranslate(change.from.toString()) + "&nbsp;"
                  : ""
              }}
            </span>
            <span v-if="change.to" class="label after">
              {{ $t("after") }}:&nbsp;</span
            >
            <template v-if="change.to && Array.isArray(change.to)">
              <span
                class="value"
                v-for="(item, index) of change.to"
                :key="index"
              >
                {{ index !== 0 ? "," : "" }}
                {{ item ? $serverTranslate(item.toString()) + "&nbsp;" : "" }}
              </span>
            </template>
            <span v-else-if="change.to" class="value">
              {{
                change.to
                  ? $serverTranslate(change.to.toString()) + "&nbsp;"
                  : ""
              }}
            </span>
          </p>
          <p class="signature">
            <span v-if="slotProps.item.createdBy" class="label">
              {{ $t("updatedBy") }}&nbsp;
            </span>
            <span v-if="slotProps.item.createdBy" class="value">
              {{
                slotProps.item.createdBy
                  ? $serverTranslate(slotProps.item.createdBy) + "&nbsp;"
                  : ""
              }}
            </span>
            <span
              v-if="slotProps.item.createdBy && slotProps.item.createdAt"
              class="label"
              >{{ $t("at").toLocaleLowerCase() }}&nbsp;</span
            >
            <span v-if="slotProps.item.createdAt" class="value">
              {{ $displayDateTime(slotProps.item.createdAt) }}
            </span>
          </p>
        </div>
        <div
          v-if="props.showTransferButton && slotProps.item.canRevert"
          class="flex flex-grow-1 mt-2 lg:mt-0"
        >
          <div class="flex-grow-0 lg:flex-grow-1"></div>
          <Button
            :label="$t('revertTransfer')"
            icon="pi pi-undo icon-fix"
            class="p-button p-button-warning p-button-sm mx-auto"
            @click="emit('revert', slotProps.item.id)"
          />
        </div>
      </div>
    </template>
  </Timeline>
</template>

<script setup lang="ts">
import type { PropType } from "vue";
import type { StudentTransaction } from "@/utils/types";
import Button from "primevue/button";
import Timeline from "primevue/timeline";

// Define Component Inputs (Props)
const props = defineProps({
  transactions: {
    type: Object as PropType<StudentTransaction[]>,
    default: undefined,
  },
  showTransferButton: {
    type: Boolean,
    default: false,
  },
});

// Define Component Outputs (Emits)
const emit = defineEmits(["revert"]);
</script>

<style lang="scss" scoped>
.labeled-value {
  background: hsl(282, 84%, 97%);
  border-width: 0px;
  border-inline-start: 2px solid var(--primary-color);
  background-color: var(--surface-50);
  border-radius: 0.35rem;
  text-align: start;
  margin-block-end: 0.5rem;
  padding: 0.5rem;
  p {
    margin: 0px;
    line-height: 1.25rem;
    font-size: 0.9rem;
  }
  .label {
    font-weight: normal;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    &.after {
      margin-inline-start: 0.5rem;
    }
  }
  .value {
    font-weight: bold;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }
  .title {
    margin-block-end: 0.25rem;
  }
  .changes {
    padding-inline-start: 1rem;
    font-size: 0.8rem;
  }
  .signature {
    font-size: 0.7rem;
  }
}
.custom-marker {
  display: flex;
  width: 2rem;
  height: 2rem;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  border-radius: 50%;
  z-index: 1;
  background: var(--primary-color);
}

::v-deep(.p-timeline-event-content),
::v-deep(.p-timeline-event-opposite) {
  line-height: 1;
}

::v-deep(.p-timeline-event-opposite) {
  flex: 0;
}

@media screen and (max-width: 960px) {
  ::v-deep(.customized-timeline) {
    .p-timeline-event:nth-child(even) {
      flex-direction: row !important;
    }
  }
}
</style>
