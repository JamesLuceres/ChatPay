<!-- src/pages/RoomPage.vue -->
<template>
  <div class="room-page column no-scroll">
    <!-- You can replicate a header similar to HomePage, or adapt as needed -->
    <div class="room-header row items-center bg-grey-3 q-px-md q-py-sm">
      <q-btn round dense flat icon="arrow_back" @click="$router.push('/home')" />
      <q-space />
      <span class="text-h6">Room {{ roomId }}</span>
      <q-space />
      <q-btn round dense flat icon="more_vert" />
    </div>

    <!-- Chat messages area (scrollable) -->
    <q-scroll-area class="room-scroll">
      <div class="q-pa-md">
        <!-- Render actual messages for roomId here -->
        <div class="text-caption text-grey-6">Messages for room {{ roomId }} would go here.</div>
      </div>
    </q-scroll-area>

    <!-- Input field at the bottom -->
    <div class="room-input row items-center bg-grey-2 q-px-md q-py-sm">
      <q-input
        v-model="newMsg"
        placeholder="Type a message"
        class="flex-grow"
        rounded
        dense
        outlined
      />
      <q-btn round dense flat icon="send" @click="sendMessage" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router' // add this back if we use router <!--, useRouter-->

const route = useRoute()
// const router = useRouter()
const newMsg = ref('')

// Grab the roomId from the URL (e.g. /rooms/4)
const roomId = route.params.id

function sendMessage() {
  console.log('Sending message to room', roomId, ':', newMsg.value)
  newMsg.value = ''
}
</script>

<style scoped>
.room-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f8fa;
}
.room-header {
  flex: 0 0 auto;
}
.room-scroll {
  flex: 1 1 auto;
}
.room-input {
  flex: 0 0 auto;
}
</style>
