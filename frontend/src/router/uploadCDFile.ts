import type { RouteRecordRaw } from "vue-router";
import { ApplicationEnum } from "@/utils/enums";
import UploadCDFileVue from "@/components/uploadCDFile/UploadCDFile.vue";

// All routes related to upload student CD File Applcation should be here,
export const uploadCDFileRoutes: RouteRecordRaw[] = [
  {
    path: "/uploadCDFile",
    name: "uploadCDFile",
    component: UploadCDFileVue,
    meta: {
      application: ApplicationEnum.UPLOAD_CD_FILE,
    },
  },
];
