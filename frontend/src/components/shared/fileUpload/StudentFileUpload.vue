<template>
  <div class="mt-2 mb-2" v-if="uploadedFiles && uploadedFiles.length">
    <div
      v-for="(file, index) of uploadedFiles"
      :key="'file-' + index"
      class="p-fileupload-row uploaded-file-row"
    >
      <span
        class="m-2 pi"
        :class="file.mimetype?.startsWith('image') ? 'pi-images' : 'pi-file'"
      ></span>
      <div class="p-fileupload-filename">
        {{ file.filename }}
      </div>
      <ProgressSpinner
        v-if="(isDownloading || isDeleting) && file == currentFile"
        style="width: 40px; height: 40px"
        strokeWidth="5"
        animationDuration="1s"
      />
      <div v-else class="file-controls">
        <button
          class="p-button p-component p-button-icon-only p-button-info"
          @click="previewDownloadedFile(file)"
          :disabled="isDownloading || isDeleting"
        >
          <span class="pi pi-eye p-button-icon"></span>
        </button>
        <button
          class="p-button p-component p-button-icon-only p-button-success m-2"
          @click="downloadFile(file)"
          :disabled="isDownloading || isDeleting"
        >
          <span class="pi pi-download p-button-icon"></span>
        </button>
        <button
          v-if="props.allowDelete"
          class="p-button p-component p-button-icon-only p-button-danger m-2"
          @click="deleteFile(file)"
          :disabled="isDownloading || isDeleting"
        >
          <span class="pi pi-trash p-button-icon"></span>
        </button>
      </div>
    </div>
  </div>
  <div v-else>
    <p class="m-3">{{ $t("noAttachmentsForStudent") }}</p>
  </div>
  <div
    v-if="allowUpload"
    class="p-fileupload p-fileupload-advanced p-component"
  >
    <div class="p-fileupload-buttonbar">
      <label
        :for="`fileInput-${props.studentUniqueId}`"
        class="p-button p-component p-fileupload-choose me-2"
        :class="isUploading ? 'p-disabled' : ''"
      >
        <input
          type="file"
          :id="`fileInput-${props.studentUniqueId}`"
          :accept="allowedMimetype.join(',')"
          @change="onSelectFiles"
          :multiple="true"
          :hidden="true"
        />
        <span class="p-button-icon p-button-icon-left pi-fw pi pi-plus"></span>
        <span class="p-button-label">{{ $t("chooseAttachments") }}</span>
      </label>
      <button
        class="p-button p-component p-button-success"
        :disabled="isUploading || !selectedFiles || !selectedFiles.length"
        @click="uploadFiles"
      >
        <span class="pi pi-upload p-button-icon p-button-icon-left"> </span>
        <span class="p-button-label">{{ $t("uploadAttachments") }}</span>
      </button>
    </div>
    <div class="p-fileupload-content">
      <Message v-if="uploadErrors" severity="error">
        <div class="multiline">{{ uploadErrors }}</div>
      </Message>
      <div class="p-fileupload-files">
        <div v-if="selectedFiles && selectedFiles.length">
          <div
            v-for="(file, index) of selectedFiles"
            :key="'file-' + index"
            class="p-fileupload-row"
          >
            <span
              class="pi"
              :class="file.type.startsWith('image') ? 'pi-images' : 'pi-file'"
            ></span>
            <div class="p-fileupload-filename">
              {{ file.name }}
            </div>
            <div>{{ formatSize(file.size) }}</div>
            <div v-if="!isUploading" class="file-controls">
              <button
                class="p-button p-component p-button-icon-only p-button-info"
                @click="openPreviewWindow(file)"
              >
                <span class="pi pi-eye p-button-icon"></span>
              </button>
              <button
                class="p-button p-component p-button-icon-only p-button-danger"
                @click="onRemoveFile(index)"
              >
                <span class="pi pi-times p-button-icon"></span>
              </button>
            </div>
            <div v-else>
              <ProgressSpinner
                style="width: 40px; height: 40px"
                strokeWidth="5"
                animationDuration="1s"
              />
            </div>
          </div>
        </div>
        <div v-else class="text-center p-3">
          {{ $t("chooseAttachmentsToUpload") }}
        </div>
      </div>
    </div>
  </div>
  <div
    v-if="previewAttachment && displayPreviewWindow"
    class="p-dialog-mask p-component-overlay p-component-overlay-enter"
  >
    <div class="p-dialog p-component p-ripple-disabled">
      <div class="p-dialog-header">
        <span id="pv_id_3_header" class="p-dialog-title">
          {{ previewAttachment.name }}
        </span>
        <div class="p-dialog-header-icons">
          <button
            class="p-dialog-header-icon p-dialog-header-close p-link"
            @click="dismissPreviewWindow()"
          >
            <span class="p-dialog-header-close-icon pi pi-times"></span>
          </button>
        </div>
      </div>
      <div class="p-dialog-content">
        <p
          v-if="$isMobile() && previewAttachment.type.includes('pdf')"
          class="text-center"
        >
          {{ $t("previewNotSupportedForMobile") }}
        </p>
        <object
          v-else
          :type="previewAttachment.type"
          :data="createPreviewObject(previewAttachment)"
          width="100%"
          :height="previewAttachment.type.includes('pdf') ? '99%' : ''"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import ProgressSpinner from "primevue/progressspinner";
import Message from "primevue/message";
import { ref, type PropType, onMounted } from "vue";
import {
  showConfirmDialog,
  showErrorToastMessage,
  showToastMessage,
} from "@/utils/globals";
import { ConfirmDialogTypes, ToastTypes } from "@/utils/enums";
import type { UploadedFile } from "@/utils/types";
import { serverTranslate } from "@/utils/filters";
import { useI18n } from "vue-i18n";

// Importing Services
const { t } = useI18n();

// Define Component Inputs (Props)
const props = defineProps({
  provider: { type: Object as PropType<any> },
  studentUniqueId: { type: String },
  attachments: { type: Array as PropType<UploadedFile[]> },
  maxAttachmentsCount: { type: Number, default: 5 },
  maxAttachmentSize: { type: Number, default: 2097152 },
  allowedMimetype: {
    type: Array as PropType<string[]>,
    default: () => ["image/*", "application/pdf"],
  },
  allowUpload: { type: Boolean, default: true },
  allowDelete: { type: Boolean, default: true },
});

const uploadedFiles = ref([] as Array<UploadedFile>);
const selectedFiles = ref([] as Array<File>);
const totalSize = ref(0);
const isUploading = ref(false);
const isDeleting = ref(false);
const isDownloading = ref(false);
const uploadErrors = ref("");
const displayPreviewWindow = ref(true);
const previewAttachment = ref();
const currentFile = ref();
const downloadedFilesBlob = ref({} as { [key: string]: string });

onMounted(() => {
  if (props.attachments && props.attachments.length > 0) {
    props.attachments.forEach((attachment: UploadedFile) => {
      uploadedFiles.value.push({
        filename: attachment.filename,
        attachmentId: attachment.attachmentId,
        mimetype: attachment.mimetype,
      });
    });
  }
});

// ----- Select/Remove -----

const onSelectFiles = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (!target) return;

  const files = target.files;
  if (!files) return;

  for (const file of files) {
    const totalCount = selectedFiles.value.length + uploadedFiles.value.length;
    if (totalCount < props.maxAttachmentsCount) {
      // check file size
      if (file.size > props.maxAttachmentSize) {
        showToastMessage(
          `${file.name}: ` +
            t("maxAttachmentSize", {
              maxSize: formatSize(props.maxAttachmentSize),
            }),
          ToastTypes.WARN
        );
        continue;
      }

      // check file type
      if (!props.allowedMimetype.includes(file.type)) {
        showToastMessage(
          `${file.name}: ` +
            t("allowedAttachmentMimetype", {
              mimetype: props.allowedMimetype.join(", "),
            }),
          ToastTypes.WARN
        );
        continue;
      }

      selectedFiles.value.push(file);
      totalSize.value += parseInt(formatSize(file.size));
    } else {
      showToastMessage(
        t("maxAttachmentsCount", { maxCount: props.maxAttachmentsCount }),
        ToastTypes.WARN
      );
      break;
    }
  }

  target.value = "";
};

const onRemoveFile = (fileIndex: number) => {
  totalSize.value -= parseInt(formatSize(selectedFiles.value[fileIndex].size));
  selectedFiles.value.splice(fileIndex, 1);
};

// ----- Upload -----

const uploadFiles = async () => {
  isUploading.value = true;
  showToastMessage(t("uploadingAttachments"), ToastTypes.INFO);
  try {
    const result = await props.provider.uploadAttachments(
      props.studentUniqueId,
      selectedFiles.value
    );

    onFilesUploaded(
      result.payload.success,
      result.payload.failed,
      result.detail
    );

    isUploading.value = false;
  } catch (error) {
    showErrorToastMessage(error);
    isUploading.value = false;
  }
};

const onFilesUploaded = (
  success: Array<UploadedFile>,
  failed: Array<UploadedFile>,
  detail: string
) => {
  uploadedFiles.value.push(...success);
  const filesKeys = success.map(
    (deletedFile: UploadedFile) => deletedFile.filename + deletedFile.mimetype
  );
  selectedFiles.value = selectedFiles.value.filter(
    (selectedFile) => !filesKeys.includes(selectedFile.name + selectedFile.type)
  );
  if (failed && failed.length > 0) {
    uploadErrors.value = formatFullMessage(failed);
  } else {
    showToastMessage(detail);
  }
};

// ----- Delete -----

const deleteFile = (file: UploadedFile) => {
  showConfirmDialog(
    t("deleteAttachmentConfirmMessage", { filename: file.filename }),
    (confirm: boolean) => {
      if (confirm) {
        confirmDeleteFile(file);
      }
    },
    ConfirmDialogTypes.CONFIRM
  );
};

const confirmDeleteFile = async (file: UploadedFile) => {
  isDeleting.value = true;
  currentFile.value = file;
  showToastMessage(
    t("deletingAttachments", { filename: file.filename }),
    ToastTypes.INFO
  );
  try {
    const result = await props.provider.deleteAttachments([file]);

    onFilesDeleted(
      result.payload.success,
      result.payload.failed,
      result.detail
    );

    isDeleting.value = false;
    currentFile.value = null;
  } catch (error) {
    showErrorToastMessage(error);
    isDeleting.value = false;
    currentFile.value = null;
  }
};

const onFilesDeleted = (
  success: Array<UploadedFile>,
  failed: Array<UploadedFile>,
  detail: string
) => {
  const filesIds = success.map(
    (deletedFile: UploadedFile) => deletedFile.attachmentId
  );
  uploadedFiles.value = uploadedFiles.value.filter(
    (file: UploadedFile) => !filesIds.includes(file.attachmentId)
  );
  if (failed && failed.length > 0) {
    showErrorToastMessage(formatFullMessage(failed));
  } else {
    showToastMessage(detail);
  }
};

// ----- Download -----

const downloadFile = async (file: UploadedFile) => {
  const fileBlob = await downloadFileBlob(file);
  if (fileBlob) {
    const url = window.URL.createObjectURL(fileBlob);

    let a = document.createElement("a");
    a.href = url;
    a.download = file.filename;
    a.click();
    a.remove();

    isDownloading.value = false;
    currentFile.value = null;
  }
};

const downloadFileBlob = async (file: UploadedFile) => {
  if (!file.attachmentId) {
    return;
  }

  if (downloadedFilesBlob.value[file.attachmentId]) {
    return downloadedFilesBlob.value[file.attachmentId];
  }

  isDownloading.value = true;
  currentFile.value = file;
  showToastMessage(
    t("downloadingAttachment", { filename: file.filename }),
    ToastTypes.INFO
  );
  try {
    const result = await props.provider.downloadAttachments(file.attachmentId);
    downloadedFilesBlob.value[file.attachmentId] = result;
    isDownloading.value = false;
    currentFile.value = null;
    return result;
  } catch (error) {
    showErrorToastMessage(error);
    isDownloading.value = false;
    currentFile.value = null;
  }
};

// ----- Preview -----

const previewDownloadedFile = async (file: UploadedFile) => {
  if (!file.attachmentId) {
    return;
  }

  const fileBlob = await downloadFileBlob(file);
  if (fileBlob) {
    const fileObject = new File([fileBlob], file.filename, {
      type: file.mimetype,
    });
    openPreviewWindow(fileObject);
  }
};

const openPreviewWindow = (file: File) => {
  previewAttachment.value = file;
  displayPreviewWindow.value = true;
};

const dismissPreviewWindow = () => {
  previewAttachment.value = undefined;
  displayPreviewWindow.value = false;
};

const createPreviewObject = (file: File) => {
  return URL.createObjectURL(file);
};

// ----- Helpers -----

const formatFullMessage = (failed: Array<UploadedFile>) => {
  return failed
    .map((nextFile: UploadedFile) =>
      nextFile.message
        ? `${nextFile.filename}: ${serverTranslate(nextFile.message)}`
        : ""
    )
    .join("\n");
};

const formatSize = (sizeInBytes: number) => {
  if (sizeInBytes === 0) {
    return "0 B";
  }

  let k = 1024,
    dm = 3,
    sizes = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"],
    i = Math.floor(Math.log(sizeInBytes) / Math.log(k));

  return (
    parseFloat((sizeInBytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i]
  );
};
</script>

<style scoped lang="scss">
.w-100 {
  width: 100%;
}

.p-fileupload-buttonbar {
  display: flex;
  justify-content: space-between;
  padding: 0.5em;
}
.p-fileupload .p-fileupload-buttonbar .p-button {
  margin-right: 0;
}
.p-fileupload .p-fileupload-buttonbar .p-button:is(:first-child) {
  margin-inline-end: 0.5rem;
}
.p-fileupload-content {
  padding: 0.5rem;
}
.p-fileupload-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem !important;
}
.p-fileupload .p-fileupload-row > div {
  margin: 0.2rem !important;
  padding: 0.2rem !important;
}
.p-fileupload-buttonbar .p-fileupload-basic {
  display: inline-block;
}
.file-controls {
  display: flex;
  justify-content: end;
  padding: 0 !important;
}
.file-controls .p-button {
  margin: 0 0.5rem 0 0 !important;
}
.uploaded-file-row {
  margin: 0 !important;
  min-height: 3.6rem;
}
.uploaded-file-row:not(:last-child) {
  border-bottom: 1px solid #ccc;
}
.p-fileupload-filename {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  font-size: 1rem !important;
  line-height: 1.3;
}

.multiline {
  white-space: pre-wrap;
}

.p-button.p-button-icon-only {
  width: 2.2rem !important;
  padding: 0.6rem 0 !important;
}

// ----- preview dialog -----
.p-dialog {
  width: 100%;
  height: 100%;
  max-width: calc(100vw - 40px);
  max-height: calc(100vh - 40px);
}
.p-dialog .p-dialog-header {
  padding: 0.5rem 1rem;
  background: #f8f9fa;
}
.p-dialog .p-dialog-content {
  height: 100%;
  overflow: auto;
  padding: 0 1rem 1rem 1rem;
}
.p-dialog-mask.p-component-overlay.p-component-overlay-enter {
  z-index: 1101;
}
.p-dialog.p-component {
  width: 100vw;
  height: 100vh;
  margin: 0px;
}
</style>
