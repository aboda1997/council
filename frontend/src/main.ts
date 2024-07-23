import { createApp } from "vue";
import { createPinia } from "pinia";
import { createI18n } from "vue-i18n";
import PrimeVue from "primevue/config";
import ToastService from "primevue/toastservice";
import ConfirmationService from "primevue/confirmationservice";
import Tooltip from "primevue/tooltip";
import App from "./App.vue";
import router from "./router";
import { getI18n } from "./assets/i18n";
import { createGlobals } from "./utils/globals";
const app = createApp(App);
app.use(createPinia());
app.use(
  createI18n({
    globalInjection: true,
    legacy: false,
    ...getI18n(),
  })
);
app.use(PrimeVue);
app.use(ToastService);
app.use(ConfirmationService);
app.directive("tooltip", Tooltip);
app.use(router);
createGlobals(app);
app.mount("#app");
