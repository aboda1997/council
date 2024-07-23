import { en } from "./en";
import { ar } from "./ar";
import { useLangStore } from "@/stores/language";

export const getI18n = () => {
  const langStore = useLangStore();
  return {
    locale: langStore.lang,
    fallbackLocale: "en",
    messages: { en, ar },
  };
};

export default { en, ar };
