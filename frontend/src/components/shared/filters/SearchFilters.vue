<template>
  <PageLoader v-if="props.errorMsg" :error="props.errorMsg" :loading="false" />
  <template v-else>
    <form @submit.prevent="submitSearch()" form="searchForm" class="p-2">
      <div class="grid justify-content-start align-content-center">
        <slot
          name="simplefields"
          :filters="props.filters"
          :query="query"
          :setField="setField"
          :clearField="clearField"
          :v$="v$"
          v-if="$slots.simplefields"
        ></slot>
        <div v-else class="field mt-3 w-full lg:col-12 md:col-12 sm:col-12 m-0">
          <span class="p-float-label">
            <InputText
              id="search"
              class="w-full"
              type="text"
              v-model="query.search"
            />
            <label for="search">{{ $t("search") }}</label>
          </span>
        </div>
        <Transition name="advanced">
          <slot
            name="advancedfields"
            :filters="props.filters"
            :query="query"
            :setField="setField"
            :clearField="clearField"
            :v$="v$"
            v-if="$slots.advancedfields && showAdvancedOptions"
          ></slot>
        </Transition>
      </div>
      <div class="grid justify-content-between align-content-center pt-3 px-2">
        <div class="field-checkbox lg:m-0" v-if="$slots.advancedfields">
          <Checkbox
            id="advancedSearchToggle"
            v-model="showAdvancedOptions"
            @change="advancedOptionsToggled"
            :binary="true"
          />
          <label for="advancedSearchToggle">
            {{ $t("advancedSearchOptions") }}
          </label>
        </div>
        <div v-else></div>
        <div class="button-wrapper md:mx-0">
          <Button
            id="searchButton"
            type="submit"
            :label="$t('search')"
            icon="pi pi-search icon-fix"
            class="filter-btn p-button-sm"
            :loading="isLoading"
          >
          </Button>
          <Button
            id="clearFiltersButton"
            type="button"
            :label="$t('clearFields')"
            class="filter-btn clear-btn p-button-sm p-button-outlined"
            @click="clearAllFields"
          >
          </Button>
        </div>
      </div>
    </form>
  </template>
</template>

<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import Button from "primevue/button";
import Checkbox from "primevue/checkbox";
import InputText from "primevue/inputtext";
import PageLoader from "../basic/PageLoader.vue";
import { ref, onMounted, type PropType, type Ref, watch, useSlots } from "vue";
import useVuelidate from "@vuelidate/core";
import { useRoute, useRouter } from "vue-router";

// Component slots
const slots = useSlots();

// Importing Services
const route = useRoute();
const router = useRouter();

// Dynamic Variables
const isLoading = ref(false);
const showAdvancedOptions = ref(false);
const query: Ref<any> = ref({});

// Define Component Inputs (Props)
const props = defineProps({
  initQuery: { type: Object as PropType<any> },
  filters: { type: Object as PropType<any> },
  advancedSearchFields: { type: Array, default: () => [] },
  errorMsg: { type: String, default: () => "" },
  rules: { type: Object },
});

onMounted(() => {
  if (route.query && Object.keys(route.query).length !== 0) {
    loadRouterQuery();
    submitSearch(false);
  } else {
    query.value = { ...props.initQuery };
    setRouterQuery({ ...query.value });
  }
  emit("queryMounted", query.value);
});

// Define Component Outputs (Emitter Events)
const emit = defineEmits(["search", "clear", "queryMounted"]);

watch(
  () => [route.query],
  () => loadRouterQuery()
);

// Set up component Validation
const v$ = useVuelidate(props.rules || {}, query);

// Component Functions
const loadRouterQuery = () => {
  query.value = { ...route.query };
  showAdvancedOptions.value = query.value.showAdvancedOptions === "true";
  if (!route.query || Object.keys(route.query).length === 0) {
    clearAllFields();
    query.value = { ...props.initQuery };
  }
};

const setRouterQuery = (urlQuery: any) => {
  if (slots.advancedfields) {
    urlQuery.showAdvancedOptions = showAdvancedOptions.value.toString();
  }
  router.replace({
    query: urlQuery,
  });
};

const setField = (fieldName: string, value: any) => {
  query.value[fieldName] = value;
};

const clearField = (fieldName: string | string[]) => {
  if (typeof fieldName === "string") {
    query.value[fieldName] = null;
    v$.value[fieldName].$reset();
  } else {
    for (const field of fieldName) {
      query.value[field] = null;
      v$.value[field].$reset();
    }
  }
};

const clearAllFields = () => {
  if (props.initQuery && Object.keys(props.initQuery).length !== 0) {
    query.value = { ...props.initQuery };
  } else {
    query.value = {};
  }
  v$.value.$reset();
  const urlQuery = { ...query.value };
  setRouterQuery(urlQuery);
  emit("clear", urlQuery);
};

const advancedOptionsToggled = () => {
  for (const field of props.advancedSearchFields) {
    if (Object.keys(props.initQuery).includes(field as string)) {
      query.value[field as string] = props.initQuery[field as string];
    } else {
      clearField(field as string);
    }
  }
};

const submitSearch = async (resetFlag = true) => {
  const isValid = await v$.value.$validate();
  if (isValid) {
    const urlQuery = { ...query.value };
    setRouterQuery(urlQuery);
    emit("search", urlQuery, resetFlag);
  }
};
</script>

<style scoped lang="scss">
.filter-btn {
  max-height: 42px;
  line-height: 1;
}
.button-wrapper {
  margin-inline-start: auto;
}
.clear-btn {
  margin-inline-start: 0.5rem;
}
.advanced-enter-active,
.advanced-leave-active {
  transition: opacity 0.2s ease;
}

.advanced-enter-from,
.advanced-leave-to {
  opacity: 0;
}
</style>
