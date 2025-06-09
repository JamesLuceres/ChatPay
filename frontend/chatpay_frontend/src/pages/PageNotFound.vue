<!-- src/pages/Error404.vue -->
<template>
  <q-page class="row items-center justify-center">
    <div class="text-h4">404 • Page Not Found</div>
    <div class="text-subtitle2 q-mt-md">Sorry, we couldn’t find what you’re looking for.</div>
    <q-btn class="q-mt-lg" label="Go Back Home" color="primary" @click="$router.push('/')" />
  </q-page>
</template>

<script setup>
// Nothing special needed here
</script>

<style scoped>
/* You can add custom styling if desired */
</style>
