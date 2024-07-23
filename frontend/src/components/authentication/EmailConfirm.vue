<template>
  <div class="container flex align-items-center justify-content-center">
    <div class="p-card confirm-card w-full md:w-6 lg:w-5 xl:w-4">
      <div class="flex flex-row align-items-center justify-content-center mb-4">
        <i class="pi pi-check-circle check-logo"></i>
        <h3 class="my-0 mx-2">{{ $t("confirmEmail") }}</h3>
      </div>

      <div>
        <div class="field col-12 mb-2">
          <p>{{ $t("confirmEmailText") }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped lang="scss">
.check-logo {
  padding: 6px;
  font-size: 1.5rem;
  color: #32cd32;
}
.container {
  width: inherit;
  height: 100%;
  background: url("@/assets/svg/wave-background.svg") center center no-repeat;
  background-size: cover;
  overflow: auto;
}
.confirm-card {
  padding: 32px;
}
</style>
