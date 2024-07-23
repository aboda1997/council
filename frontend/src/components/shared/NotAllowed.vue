<template>
  <div class="centered-404-container" dir="ltr">
    <div class="error">
      <div class="number">4</div>
      <div class="illustration">
        <div class="circle"></div>
        <div class="clip">
          <div class="paper">
            <div class="face">
              <div class="eyes">
                <div class="eye eye-left"></div>
                <div class="eye eye-right"></div>
              </div>
              <div class="rosyCheeks rosyCheeks-left"></div>
              <div class="rosyCheeks rosyCheeks-right"></div>
              <div class="mouth"></div>
            </div>
          </div>
        </div>
      </div>
      <div class="number">3</div>
    </div>

    <div class="text">{{ $t("notAllowed403") }}</div>
    <Button class="button" @click="$router.back()">{{
      $t("goBack404")
    }}</Button>
  </div>
</template>

<script setup lang="ts">
import Button from "primevue/button";
</script>

<style scoped lang="scss">
/* colors */
$outline: #293b49;
$cheeks: #fdabaf;
$pink-light: #ffe0e6;
$green: #04cba0;
$green-dark: #01ac88;
$white: white;

.centered-404-container {
  font-size: 62.5%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  margin-top: -2rem;

  .error {
    transform: scale(0.625);
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-content: center;
    @media only screen and (max-width: 300px) {
      transform: scale(0.5);
    }
  }

  .number {
    font-weight: 900;
    font-size: 15rem;
    line-height: 1;
  }

  .illustration {
    position: relative;
    width: 12.2rem;
    margin: 0 2.1rem;
  }

  .circle {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 12.2rem;
    height: 11.4rem;
    border-radius: 50%;
    background-color: $outline;
  }

  .clip {
    position: absolute;
    bottom: 0.3rem;
    left: 50%;
    transform: translateX(-50%);
    overflow: hidden;
    width: 12.5rem;
    height: 13rem;
    border-radius: 0 0 50% 50%;
  }

  .paper {
    position: absolute;
    bottom: -0.3rem;
    left: 50%;
    transform: translateX(-50%);
    width: 9.2rem;
    height: 12.4rem;
    border: 0.3rem solid $outline;
    background-color: $white;
    border-radius: 0.8rem;

    &::before {
      content: "";
      position: absolute;
      top: -0.7rem;
      right: -0.8rem;
      width: 1.4rem;
      height: 1rem;
      background-color: $white;
      border-bottom: 0.3rem solid $outline;
      transform: rotate(45deg);
    }
  }

  .face {
    position: relative;
    margin-top: 2.3rem;
  }

  .eyes {
    position: absolute;
    top: 0;
    left: 2rem;
    width: 4.6rem;
    height: 0.8rem;
  }

  .eye {
    position: absolute;
    bottom: 0;
    width: 0.8rem;
    height: 0.8rem;
    border-radius: 50%;
    background-color: $outline;
    animation-name: eye;
    animation-duration: 4s;
    animation-iteration-count: infinite;
    animation-timing-function: ease-in-out;

    &-left {
      left: 0;
    }

    &-right {
      right: 0;
    }
  }

  @keyframes eye {
    0% {
      height: 0.8rem;
    }
    50% {
      height: 0.8rem;
    }
    52% {
      height: 0.1rem;
    }
    54% {
      height: 0.8rem;
    }
    100% {
      height: 0.8rem;
    }
  }

  .rosyCheeks {
    position: absolute;
    top: 1.6rem;
    width: 1rem;
    height: 0.2rem;
    border-radius: 50%;
    background-color: $cheeks;

    &-left {
      left: 1.4rem;
    }

    &-right {
      right: 1.4rem;
    }
  }

  .mouth {
    position: absolute;
    top: 3.1rem;
    left: 50%;
    width: 1.6rem;
    height: 0.2rem;
    border-radius: 45%;
    transform: translateX(-50%);
    background-color: $outline;
  }

  .text {
    font-weight: 300;
    color: $outline;
    font-size: 1.25rem;
    text-align: center;
  }

  .button {
    margin-top: 2rem;
    max-height: 47px;
  }
}
</style>
