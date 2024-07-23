import { useLocalStorage } from "@vueuse/core";
import { defineStore } from "pinia";
import { ref, type Ref } from "vue";

export const useGeneralStore = defineStore("general", () => {
  // Data Variables in the Store
  const selectedTransferUniversity: Ref<number | undefined> = ref(
    useLocalStorage("SELECTED_TRANSFER_UNIVERSITY", -1)
  );

  return { selectedTransferUniversity };
});
