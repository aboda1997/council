import { useLangStore } from "@/stores/language";
import { useUserDataStore } from "@/stores/userData";
import type { App } from "vue";
import { ApplicationEnum, Language, RightsEnum } from "./enums";
import type { UserApplication } from "./types";
import * as XLSX from "xlsx";

let langStore: { lang: string } = { lang: "" };
let userStore: { userApplications: UserApplication[] } = {
  userApplications: [],
};

// Filter or pipe to translate incoming data from the backend
// dependin on the language of the interface.
export const serverTranslate = (
  token: string,
  langCode: string = langStore.lang
): string => {
  if (langCode === Language.ARABIC) {
    return token.split("|")[0] || token.split("|")[1];
  } else if (langCode === Language.ENGLISH) {
    return token.split("|")[1] || token.split("|")[0];
  } else {
    return "";
  }
};

// Filter to limit the number of words of given text
// Depending on the character limit set.
export const limitWordsByChar = (token: string, charLimit: number) => {
  if (!token || token === undefined) {
    return "";
  }
  if (token && token.trim().length > charLimit) {
    const tokenParts = token.trim().split(" ");
    let limitedToken = "";
    for (const part of tokenParts) {
      if (limitedToken.length + part.length >= charLimit) {
        break;
      }
      limitedToken = limitedToken + " " + part;
    }
    return limitedToken;
  }
  return token.trim();
};

// Filter or pipe to allow trimming string in similar manner to other filter.
export const trim = (token: string): string => {
  return token.trim();
};

// Filter or pipe that returns whether or not user can access a given app with a given right.
export const hasPermission = (
  appId: ApplicationEnum,
  rightId: RightsEnum = RightsEnum.VIEW
): boolean => {
  const application = userStore.userApplications.find(
    (app) => app.id === appId
  );
  if (application) {
    return application.rights.indexOf(rightId) !== -1;
  }
  return false;
};

// Evaluates a string that can be passed as a function.
export const evaluateStringValue = (token?: string | (() => string)) => {
  if (!token || token === undefined) {
    return "";
  }
  if (token instanceof Function) {
    return token();
  }
  return token;
};

// Print a specific element that is currently on display
export const printVueHtmlElement = (elementId: string) => {
  const element = window.document.getElementById(elementId);

  // Get all stylesheets HTML
  let stylesHtml = "";
  for (const node of [
    ...document.querySelectorAll('link[rel="stylesheet"], style'),
  ]) {
    stylesHtml += node.outerHTML;
  }

  if (!element) {
    alert(`Element to print #${elementId} not found!`);
    return;
  }

  const ifprint = document.createElement("iframe");
  document.body.appendChild(ifprint);
  ifprint.setAttribute("style", "height:0;width:0;");

  const content = ifprint.contentWindow;

  const bodyLangClass = langStore.lang == "ar" ? "lang-ar" : "lang-en";

  content?.document.write(`
    <html>
      <head>
        ${stylesHtml}
        <title>${window.document.title}</title>
      </head>
      <body class="${bodyLangClass}">
        ${element.innerHTML}
      </body>
    </html>
  `);

  setTimeout(() => {
    content?.document.close();
    content?.focus();
    content?.print();
    content?.close();
    document.body.removeChild(ifprint);
  }, 500);

  return true;
};

// Exports all tables in a specific element that is currently on display
export const exportExcelHtmlElement = (
  elementId: string,
  filename = "CPNU_File",
  type: XLSX.BookType = "xlsx"
) => {
  // Generate file timestamp
  const date = new Date(Date.now());
  const minutes = ("0" + date.getMinutes()).slice(-2);
  const hours = date.getHours();
  const day = ("0" + date.getDate()).slice(-2);
  const month = ("0" + (date.getMonth() + 1)).slice(-2); //January is 0!
  const year = date.getFullYear();
  const timestamp =
    day + "-" + month + "-" + year + "_" + hours + "-" + minutes + "_";
  /* eslint-disable @typescript-eslint/no-explicit-any */
  const XLSX_lib = XLSX as any;
  const data = document.getElementById(elementId);
  const file = (XLSX_lib.utils as XLSX.XLSX$Utils).table_to_book(data, {
    sheet: "sheet1",
  });
  XLSX_lib.write(file, { bookType: type, bookSST: true, type: "base64" });
  XLSX_lib.writeFile(file, timestamp + filename + "." + type);
};

export const displayDateTime = (token: string | Date) => {
  if (token) {
    const date = new Date(token);
    const minutes = ("0" + date.getMinutes()).slice(-2);
    const hours = date.getHours();
    const hours12h = hours % 12 ? ("0" + (hours % 12)).slice(-2) : 12;
    const ampm = hours >= 12 ? "م|pm" : "ص|am";
    const day = ("0" + date.getDate()).slice(-2);
    const month = ("0" + (date.getMonth() + 1)).slice(-2); //January is 0!
    const year = date.getFullYear();
    return (
      day +
      "-" +
      month +
      "-" +
      year +
      " | " +
      hours12h +
      ":" +
      minutes +
      " " +
      serverTranslate(ampm)
    );
  }
  return "";
};

const isMobile = () => {
  if (
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    )
  ) {
    return true;
  } else {
    return false;
  }
};

// Adds the filters to the Vue app so they can be used in templates.
export const createFilters = (app: App) => {
  langStore = useLangStore();
  userStore = useUserDataStore();
  app.config.globalProperties.$serverTranslate = serverTranslate;
  app.config.globalProperties.$limitWordsByChar = limitWordsByChar;
  app.config.globalProperties.$trim = trim;
  app.config.globalProperties.$hasPermission = hasPermission;
  app.config.globalProperties.$evaluateStringValue = evaluateStringValue;
  app.config.globalProperties.$printVueHtmlElement = printVueHtmlElement;
  app.config.globalProperties.$exportExcelHtmlElement = exportExcelHtmlElement;
  app.config.globalProperties.$displayDateTime = displayDateTime;
  app.config.globalProperties.$isMobile = isMobile;
};

// Registers filters in this interface so typescript see them in the various vue files.
declare module "@vue/runtime-core" {
  interface ComponentCustomProperties {
    $serverTranslate: typeof serverTranslate;
    $limitWordsByChar: typeof limitWordsByChar;
    $trim: typeof trim;
    $hasPermission: typeof hasPermission;
    $evaluateStringValue: typeof evaluateStringValue;
    $printVueHtmlElement: typeof printVueHtmlElement;
    $exportExcelHtmlElement: typeof exportExcelHtmlElement;
    $displayDateTime: typeof displayDateTime;
    $isMobile: typeof isMobile;
  }
}
