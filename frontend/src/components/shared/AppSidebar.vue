<template>
  <Transition name="menu">
    <div v-if="props.menuOpen && isLargeScreen" class="menu-wrapper">
      <PanelMenu
        ref="menuRef"
        class="sidebar-menu"
        :model="items"
        v-model:expandedKeys="keys"
      />
    </div>
  </Transition>
  <Sidebar
    v-if="!isLargeScreen"
    v-model:visible="menuOpen"
    class="app-mobile-sidebar"
    :class="sidebarCSS"
    :position="mobileMenuPos"
  >
    <div :class="cssLang">
      <PanelMenu
        class="sidebar-menu mobile-menu"
        :model="items"
        v-model:expandedKeys="keys"
      />
    </div>
  </Sidebar>
</template>

<script setup lang="ts">
import Sidebar from "primevue/sidebar";
import PanelMenu from "primevue/panelmenu";
import type { MenuItem } from "primevue/menuitem";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { ref, computed, watch, onMounted } from "vue";
import { useMediaQuery } from "@vueuse/core";
import { useUserDataStore } from "@/stores/userData";
import { useLangStore } from "@/stores/language";
import { Language } from "@/utils/enums";
import { serverTranslate } from "@/utils/filters";

// Importing Services
const { t } = useI18n();
const route = useRoute();
const langStore = useLangStore();
const userDataStore = useUserDataStore();

// UI states
const defaultKeys: { [id: string]: boolean } = {};
const keys = ref(defaultKeys);
const menuRef = ref(null);
const menuOpen = ref(false);
const isLargeScreen = useMediaQuery("(min-width: 768px)");
const mobileMenuPos = computed(() =>
  langStore.locale === Language.ARABIC ? "right" : "left"
);
const sidebarCSS = computed(() =>
  langStore.locale === Language.ARABIC ? "sidebar-ar" : "sidebar-en"
);
const cssLang = computed(() =>
  langStore.locale === Language.ARABIC ? "lang-ar" : "lang-en"
);

// On Mounted Behaviour
onMounted(async () => {
  updateSideBarRoutes();
  expandNode();
});

// update SideBar When Permission Change
watch(
  () => [userDataStore.userApplications, route.fullPath],
  () => updateSideBarRoutes()
);

// Menu Button Logic
const props = defineProps(["menuOpen"]);
watch(
  () => props.menuOpen,
  () => {
    if (!isLargeScreen.value) {
      menuOpen.value = !menuOpen.value;
    }
  }
);

// Menu Items
const defaultRoutes: MenuItem[] = [
  {
    key: "home",
    icon: "pi pi-home icon-fix",
    label: () => {
      return t("homepage");
    },
    to: "/",
  },
];
const items = ref(defaultRoutes);
// Updating Side Bar Routes from User Permissions
const updateSideBarRoutes = () => {
  const userRoutes: MenuItem[] = userDataStore.appCategories.map((category) => {
    return {
      key: "category" + category.id,
      icon: "pi pi-" + category.icon + " icon-fix",
      class: "category-menu",
      label: () => {
        return serverTranslate(category.displayName);
      },
      items: userDataStore.userApplications
        .filter((app) => app.categoryId === category.id)
        .map((app) => {
          return {
            key: "app" + app.id,
            icon: "pi pi-" + app.icon + " icon-fix",
            label: () => {
              return serverTranslate(app.displayName);
            },
            className: route.fullPath.includes(app.name) ? "active-app" : "",
            to: "/" + app.name,
          };
        }),
    };
  });
  items.value = [...defaultRoutes, ...userRoutes];
};

// Other Component Functions
const expandNode = () => {
  if (route.meta.application) {
    const currentApp = userDataStore.userApplications.find(
      (app) => app.id === route.meta.application
    );
    if (currentApp) {
      keys.value["category" + currentApp.categoryId] = true;
    }
  }
};
</script>

<style lang="scss">
.menu-wrapper {
  max-width: 100vh;
  height: 100%;
  background: transparent;
  border-radius: 0;
  border-right: 1px solid #dee2e6;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.lang-ar .menu-wrapper {
  border-right: none;
  border-left: 1px solid #dee2e6;
}
.side-bar-logo {
  padding: 0 1.25rem;
}
.side-bar-logo {
  padding: 0.05rem 1.25rem;
  margin: 0;
}
.sidebar-menu.p-panelmenu {
  width: 225px;
  font-size: 0.88rem !important;
  overflow-y: auto;
  &::-webkit-scrollbar {
    width: 5px;
  }
  &::-webkit-scrollbar-track {
    background: #f1f1f1;
  }
  &::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 3px;
  }
  &::-webkit-scrollbar-thumb:hover {
    background: #555;
  }
  .p-panelmenu-header {
    > a {
      padding: 0.75rem;
      background: none;
      border-radius: 0;
      border: none;
      border-inline-start: 2px #dee2e6 solid;
      background: #fff;
      box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1),
        0 1px 2px 0 rgba(0, 0, 0, 0.06);
      border-radius: 6px;
      .p-menuitem-icon {
        color: var(--secondary-color) !important;
      }
    }
    .router-link-active-exact {
      border-inline-start: 2px var(--primary-color) solid !important;
      background-color: rgba(201, 201, 201, 0.3);
      color: var(--primary-color);
      > .p-menuitem-text {
        color: var(--primary-color);
      }
    }
    &.p-highlight > a {
      color: #6c757d;
    }
  }
  .category-menu {
    .p-panelmenu-header.p-highlight > a {
      color: #343a40;
      border-inline-start: 2px var(--primary-color) solid !important;
    }
  }
  .p-menuitem:nth-last-child(1) > a {
    border-bottom-right-radius: 6px;
    border-bottom-left-radius: 6px;
  }
  .p-menuitem > a {
    padding: 0.75rem 1rem !important;
    border-inline-start: 2px #dee2e6 solid;
    background: #fff;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    &.p-menuitem-link .p-menuitem-icon {
      color: var(--secondary-color) !important;
    }
  }
  .p-menuitem .router-link-active-exact,
  .p-menuitem.active-app > a {
    border-inline-start: 2px var(--primary-color) solid;
    background-color: rgba(201, 201, 201, 0.3);
    > .p-menuitem-text {
      color: var(--primary-color) !important;
    }
  }
  .p-submenu-list,
  .p-submenu-list:not(.p-panelmenu-root-submenu) {
    padding: 0;
    padding-inline-start: 9px;
    padding-inline-end: 4px;
  }
  .p-panelmenu-header:not(.p-highlight):not(.p-disabled) > a:hover {
    background-color: rgba(201, 201, 201, 0.4) !important;
  }
  .p-panelmenu-header:not(.p-highlight):not(.p-disabled)
    > a.router-link-active-exact:hover {
    border-inline-start: 2px var(--primary-color) solid;
    background-color: rgba(201, 201, 201, 0.4) !important;
    > .p-menuitem-icon,
    .p-menuitem-text {
      color: var(--primary-color);
    }
  }
  .p-panelmenu-panel {
    margin: 0.5rem;
  }
  .p-menuitem-icon,
  .p-panelmenu-icon {
    margin-right: 0.325rem;
  }
  .p-panelmenu-content {
    padding: 0;
    border: none;
    border-radius: 0;
    margin-bottom: 0;
    background: transparent;
  }
  .p-panelmenu-content .p-menuitem .p-menuitem-link:focus {
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  }
  .p-panelmenu-header-link:focus {
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  }
}

.lang-ar,
.sidebar-ar {
  .sidebar-menu.p-panelmenu {
    .p-panelmenu-header {
      .router-link-active-exact {
        border-left: none;
        border-right: 2px var(--primary-color) solid;
      }
    }
    .p-menuitem .router-link-active-exact,
    .p-menuitem.active-app > a {
      border-left: none;
      border-right: 2px var(--primary-color) solid;
    }
    .p-panelmenu-header:not(.p-highlight):not(.p-disabled)
      > a.router-link-active-exact:hover {
      border-left: none;
      border-right: 2px var(--primary-color) solid;
    }
    .p-menuitem-icon,
    .p-panelmenu-icon {
      margin-left: 0.325rem;
      margin-right: 0;
    }
  }
  .p-panelmenu
    .p-panelmenu-content
    .p-menuitem
    .p-menuitem-link
    .p-menuitem-icon {
    border: none !important;
    margin-right: 0;
  }
  .p-panelmenu
    .p-panelmenu-content
    .p-submenu-list:not(.p-panelmenu-root-submenu) {
    padding: 0 1rem 0 0;
  }
}

.sidebar-menu.p-panelmenu.mobile-menu {
  width: 100%;
}
.p-sidebar.app-mobile-sidebar {
  background-color: var(--layout-background-color);
  .p-sidebar-content {
    padding: 0.25rem;
  }
}
.menu-enter-active,
.menu-leave-active {
  transition: opacity 0.25s ease, width 0.25s ease-in-out;
  width: 225px;
}

.menu-enter-from,
.menu-leave-to {
  width: 0px;
  opacity: 0;
}
</style>
