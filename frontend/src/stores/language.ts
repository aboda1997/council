import { Language } from "@/utils/enums";
import { getAppLocale, switchAppLocale } from "@/utils/globals";
import { useLocalStorage } from "@vueuse/core";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

// Store for holding data related to the system language
export const useLangStore = defineStore("language", () => {
  // Data Variables in the Store
  const lang = ref(useLocalStorage("lang", Language.ARABIC));

  // Computed Variables in the Store
  const locale = computed(() => getAppLocale());

  const dir = computed(() =>
    locale.value === Language.ARABIC ? "rtl" : "ltr"
  );

  // Functions running on Variables in the Store.
  const changeLang = (newLang?: string) => {
    document.body.className = "";
    if (newLang) {
      lang.value = newLang;
    } else if (lang.value === Language.ARABIC) {
      lang.value = Language.ENGLISH;
    } else {
      lang.value = Language.ARABIC;
    }
    document.body.classList.add("lang-" + lang.value);
    switchAppLocale(lang.value);
  };

  return { lang, locale, dir, changeLang };
});
