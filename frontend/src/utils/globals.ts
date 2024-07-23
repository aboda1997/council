import type { App } from "vue";
import { ConfirmDialogTypes, InfoDialogTypes, ToastTypes } from "./enums";
import axios from "axios";
import type { AxiosError } from "axios";
import { createFilters, serverTranslate } from "./filters";
import type { DialogCallback } from "./types";

const defaultToasterLifeTime = 5000;
let app: App;

// Adds Any new useful global functions to Vue to be accessable in templates
// Ex (filters like serverTranslate)ables to
export const createGlobals = (appRef: App) => {
  app = appRef;
  createFilters(app);
};

// Global Function to Change the Application Locale
// (Usually run from with the langStore)
export const switchAppLocale = (lang: string) => {
  app.config.globalProperties.$i18n.locale = lang;
};

export const getAppLocale = () => {
  return app.config.globalProperties.$i18n.locale;
};

export const redirectToLogin = () => {
  const prevPath = app.config.globalProperties.$route.path;
  const prevQuery = app.config.globalProperties.$route.query;
  if (prevPath !== "/login") {
    app.config.globalProperties.$router.push({
      path: "/login",
      query: {
        redirect: prevPath,
        ...prevQuery,
      },
    });
  } else {
    app.config.globalProperties.$router.push("/");
  }
};

// Global Toaster Service that Can be Access for any component.
export const showToastMessage = (
  detail: string,
  type: ToastTypes = ToastTypes.SUCCESS,
  lifeTime: number = defaultToasterLifeTime
): void => {
  let title = app.config.globalProperties.$t("successful");
  switch (type) {
    case ToastTypes.WARN: {
      title = app.config.globalProperties.$t("warning");
      break;
    }
    case ToastTypes.INFO: {
      title = app.config.globalProperties.$t("info");
      break;
    }
    case ToastTypes.ERROR: {
      title = app.config.globalProperties.$t("error");
      break;
    }
  }
  app.config.globalProperties.$toast.add({
    severity: type,
    summary: title,
    detail: serverTranslate(detail),
    life: lifeTime,
    group: "global",
  });
};

// Global Toaster Service made for request error handling
// Can be extended for other types of errors over time.
export const showErrorToastMessage = (
  err: AxiosError | string | unknown,
  toastType = ToastTypes.ERROR,
  lifeTime: number = defaultToasterLifeTime,
  clearAll = true
) => {
  if (clearAll) {
    clearToastMessages();
  }
  if (axios.isAxiosError(err)) {
    const payload = err as AxiosError;
    if (payload.response && payload.response.data.detail) {
      showToastMessage(payload.response.data.detail, toastType, lifeTime);
    } else {
      showToastMessage(
        app.config.globalProperties.$t("internalError"),
        toastType,
        lifeTime
      );
    }
  } else if (typeof err === "string") {
    showToastMessage(err as string, toastType, lifeTime);
  }
};

// Global Confirm Dialog Service for various types of dialogs
// Before executing some function (Optional)
export const showGlobalDialog = (
  detail: string,
  callBack: DialogCallback | null = null,
  type: ConfirmDialogTypes | InfoDialogTypes = ConfirmDialogTypes.CONFIRM
) => {
  const okLabel = app.config.globalProperties.$t("ok");
  const yesLabel = app.config.globalProperties.$t("yes");
  const noLabel = app.config.globalProperties.$t("no");
  let acceptLabel = yesLabel;
  let header = app.config.globalProperties.$t("normalConfirm");
  let icon = "pi pi-question-circle";
  let acceptClass = "p-button-sm p-button-primary";
  let rejectClass = "p-button-sm p-button-primnoLabelary p-button-text";
  let blockExecution = false;
  switch (type) {
    case ConfirmDialogTypes.WARNING: {
      header = app.config.globalProperties.$t("warnConfirm");
      icon = "pi pi-exclamation-circle icon-fix";
      acceptClass = "p-button-sm p-button-warning";
      rejectClass = "p-button-sm p-button-warning p-button-text";
      break;
    }
    case ConfirmDialogTypes.CRITICAL: {
      header = app.config.globalProperties.$t("criticalConfirm");
      icon = "pi pi-exclamation-triangle icon-fix";
      acceptClass = "p-button-sm p-button-danger";
      rejectClass = "p-button-sm p-button-danger p-button-text";
      break;
    }
    case InfoDialogTypes.ERROR: {
      header = app.config.globalProperties.$t("error");
      icon = "hidden";
      acceptClass = "p-button-sm p-button-danger p-button-text m-auto";
      rejectClass = "hidden";
      acceptLabel = okLabel;
      break;
    }
    case InfoDialogTypes.INFO: {
      header = app.config.globalProperties.$t("info");
      icon = "hidden";
      acceptClass = "p-button-primary p-button-text m-auto";
      rejectClass = "hidden";
      acceptLabel = okLabel;
      break;
    }
  }
  app.config.globalProperties.$confirm.require({
    message: serverTranslate(detail),
    header: header,
    icon: icon,
    acceptLabel: acceptLabel,
    rejectLabel: noLabel,
    acceptClass: acceptClass,
    rejectClass: rejectClass,
    accept: () => {
      if (callBack !== null) {
        if (!blockExecution) {
          blockExecution = true;
          callBack(true);
        }
      }
    },
    reject: () => {
      if (callBack !== null) {
        if (!blockExecution) {
          blockExecution = true;
          callBack(false);
        }
      }
    },
  });
};

export const showConfirmDialog = (
  detail: string,
  callBack: DialogCallback | null = null,
  type: ConfirmDialogTypes = ConfirmDialogTypes.CONFIRM
) => {
  showGlobalDialog(detail, callBack, type);
};

export const showInfoDialog = (
  detail: string,
  callBack: DialogCallback | null = null
) => {
  showGlobalDialog(detail, callBack, InfoDialogTypes.INFO);
};

export const showErrorDialog = (
  detail: string,
  callBack: DialogCallback | null = null
) => {
  showGlobalDialog(detail, callBack, InfoDialogTypes.ERROR);
};

// Removes all current toast messages
export const clearToastMessages = () => {
  app.config.globalProperties.$toast.removeAllGroups();
};
