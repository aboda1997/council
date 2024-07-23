<template>
  <div class="layout-topbar shadow-0">
    <div class="topbar-left">
      <Button class="hamburger-button top-bar-button" @click="toggleMenu">
        <i class="pi pi-bars"></i>
      </Button>
      <Button
        v-if="!isLargeScreen || isLogoVisible || true"
        class="icon-button top-bar-button"
        @click="navigateToHome"
      >
        <img
          class="icon-img"
          src="@/assets/imgs/logo.png"
          alt="Council of Private and National Universities (CPNU)"
        />
        <h4 v-if="isLargeScreen" class="icon-title">{{ $t("pucName") }}</h4>
      </Button>
    </div>
    <div class="topbar-right">
      <ul class="topbar-menu">
        <li class="lang-item" v-if="isLargeScreen">
          <Button
            v-tooltip.bottom="{ value: $t('changeLang') }"
            class="menu-button top-bar-button"
            @click="switchLang"
          >
            <div class="flex align-items-baseline" dir="ltr">
              <i class="pi pi-globe"></i>
              <span class="font-xsmall">{{ $t("switchToLang") }}</span>
            </div>
          </Button>
        </li>
        <li class="seperator" v-if="isLargeScreen"></li>
        <li class="settings-item" v-if="isLargeScreen">
          <Button
            v-tooltip.bottom="{ value: $t('settings') }"
            class="menu-button top-bar-button"
          >
            <div class="flex align-items-baseline">
              <i class="pi pi-cog icon-fix"></i>
            </div>
          </Button>
        </li>
        <li class="seperator" v-if="isLargeScreen"></li>
        <li class="user-item">
          <Button
            v-if="isLargeScreen"
            v-tooltip.bottom="{ value: $t('user') }"
            class="menu-button top-bar-button"
            @click="toggleUserMenu"
          >
            <div class="flex align-items-baseline">
              <i class="pi pi-user"></i>
              <p class="font-small max-char">
                {{
                  $limitWordsByChar(
                    $serverTranslate(userDataStore.userData.fullname || ""),
                    16
                  )
                }}
              </p>
              <i class="font-xsmall pi pi-chevron-down"></i>
            </div>
          </Button>
          <Button
            v-if="!isLargeScreen"
            v-tooltip.bottom="{ value: $t('more') }"
            class="menu-button dropdown-button top-bar-button"
            @click="toggleUserMenu"
          >
            <div class="flex align-items-baseline">
              <i class="pi pi-ellipsis-v icon-fix"></i>
            </div>
          </Button>
          <Menu
            id="top_bar_menu"
            :class="['top-bar-menu', componentCSS]"
            ref="topBarMenu"
            :model="isLargeScreen ? userMenuItems : topBarMenuItems"
            :popup="true"
          ></Menu>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import Button from "primevue/button";
import Menu from "primevue/menu";
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useMediaQuery } from "@vueuse/core";
import { useUserDataStore } from "@/stores/userData";
import { useLangStore } from "@/stores/language";
import { Language } from "@/utils/enums";
import { serverTranslate, limitWordsByChar } from "@/utils/filters";

// Importing Services
const { t } = useI18n();
const router = useRouter();
const langStore = useLangStore();
const userDataStore = useUserDataStore();

// UI states
const emit = defineEmits(["menuToggleEvent"]);
const isLogoVisible = ref(false);
const isLargeScreen = useMediaQuery("(min-width: 768px)");
const componentCSS = computed(() =>
  langStore.lang === Language.ARABIC ? "p-component-ar" : "p-component-en"
);

// User Submenu Ref and Items
const userMenuItems = [
  {
    icon: "pi pi-book icon-fix",
    label: () => {
      return t("profile");
    },
    command: () => {
      navigateToProfile();
    },
  },
  {
    icon: "pi pi-sign-out icon-fix",
    label: () => {
      return t("logout");
    },
    command: () => {
      signOut();
    },
  },
];
const optionsMenuItems = [
  {
    icon: "pi pi-globe icon-fix",
    label: () => {
      return t("changeLang");
    },
    command: () => {
      switchLang();
    },
  },
  {
    icon: "pi pi-cog icon-fix",
    label: () => {
      return t("settings");
    },
  },
];

const topBarMenu = ref();
const topBarMenuItems = ref([
  {
    label: () => {
      return limitWordsByChar(
        serverTranslate(userDataStore.userData.fullname || ""),
        16
      );
    },
    items: [...optionsMenuItems, ...userMenuItems],
  },
]);

// Component Functions
const toggleMenu = () => {
  isLogoVisible.value = !isLogoVisible.value;
  emit("menuToggleEvent");
};
const switchLang = () => {
  langStore.changeLang();
};
const toggleUserMenu = (event: object) => {
  topBarMenu.value.toggle(event);
};
const navigateToHome = () => {
  router.push("/");
};
const navigateToProfile = () => {
  router.push("/profile");
};
const signOut = () => {
  userDataStore.resetUserData();
  router.push("/login");
};
</script>

<style scoped lang="scss">
.layout-topbar {
  background: var(--topbar-background-color);
  height: 48px;
  padding: 0;
  border-bottom: 1px solid #dee2e6;
  width: 100%;
  top: 0;
  left: 0;
  z-index: 5;
  display: -ms-flexbox;
  display: flex;
  -ms-flex-align: center;
  align-items: center;
  -ms-flex-pack: justify;
  justify-content: space-between;
  transition: none;
  h1 {
    margin: 0 0.375rem;
  }
  .top-bar-button {
    padding: 0.75rem;
    color: var(--topbar-color);
    background-color: transparent;
    border-color: transparent;
    &:hover {
      color: var(--surface-a);
      background-color: #ffffff33;
    }
    &:focus {
      box-shadow: none;
    }
  }
  .seperator {
    border-left: var(--surface-a) 2px solid;
    height: 20px;
    border-radius: 5px;
  }
  .icon-button {
    padding: 0;
    .icon-img {
      height: 2.5rem;
    }
    .icon-title {
      margin: auto;
      margin-inline-start: 0.5rem;
    }
    @media screen and (max-width: 768px) {
      margin: 0 auto;
    }
  }
  .menu-button {
    padding: 0.5rem 0.25rem;
    i {
      font-size: 1rem;
    }
    .font-small {
      font-weight: 600;
      font-size: 0.85rem;
      margin: auto 0.2rem;
      line-height: 1;
    }
    .font-xsmall {
      font-weight: bold;
      font-size: 0.65rem;
    }
  }
  .hamburger-button,
  .dropdown-button {
    padding: 0.75rem;
    margin: 0 0.25rem;
  }
  .topbar-left {
    display: -ms-flexbox;
    display: flex;
    -ms-flex-align: center;
    align-items: center;
    flex-grow: 1;
    .horizontal-logo {
      display: none;
    }
  }
  .topbar-right {
    padding: 0 0.5rem;
    @media screen and (max-width: 768px) {
      padding: 0;
    }
  }
  .topbar-menu {
    margin: 0;
    padding: 0;
    list-style-type: none;
    display: -ms-flexbox;
    display: flex;
    -ms-flex-align: center;
    align-items: center;
    margin: 0;
    padding: 0;
    list-style-type: none;
    display: -ms-flexbox;
    display: flex;
    -ms-flex-align: center;
    align-items: center;
    > li {
      margin: 0 0.125rem;
      position: relative;
      &:first {
        margin-left: 0;
      }
      > a {
        width: 2rem;
        height: 2rem;
        text-align: center;
        color: #495057;
        overflow: hidden;
        border-radius: 4px;
        transition: background-color 0.2s, box-shadow 0.2s;
        display: block;
        position: relative;
        cursor: pointer;
        user-select: none;
        outline: 0 none;
        &:hover {
          background: #e9ecef;
        }
        &:focus {
          box-shadow: 0 0 0 0.2rem #bbdefb;
        }
        i {
          line-height: inherit;
          font-size: 1.5rem;
        }
      }
      > ul {
        display: none;
        position: absolute;
        background: #ffffff;
        list-style: none;
        margin: 0;
        padding: 1rem;
        top: 3.25rem;
        right: 0;
        z-index: 999;
        min-width: 250px;
        border: 0 none;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.2),
          0 4px 5px 0 rgba(0, 0, 0, 0.14), 0 1px 10px 0 rgba(0, 0, 0, 0.12);
        animation-duration: 0.12s;
        animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
        border-radius: 4px;
        transform-origin: center top;
      }
    }
  }
}
</style>
