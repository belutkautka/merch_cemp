<script setup lang="ts">
</script>

<template class="app">
  <div class="main">
    <router-view />
  </div>
</template>

<style scoped>
  .main{
    max-width: 500px;
    width: 100vw;
    background-color: var(--white);
    min-height: 100vh;
    position: relative;
    top: -10px;
  }
</style>
