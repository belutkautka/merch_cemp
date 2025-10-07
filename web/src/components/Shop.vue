<script setup lang="ts">

import header from "../../public/header.jpg";
import Menu from "./Menu.vue";
</script>

<template>
  <img :src="header" class="header" alt="bad bar"/>
  <div class="box">
    <Menu/>
  </div>
</template>

<style scoped>
.header{
  width: 100%;
}

.box{
  background-color: var(--white);
  width: calc(100% - 40px);
  position: relative;
  display: inline-box;
  top: -50px;
  min-height: 100vh;
  border-radius: 32px;
  padding: 20px;
}
</style>