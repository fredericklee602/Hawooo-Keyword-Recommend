<template>
  <div class="home">
    <img alt="Sheep logo" class="logo" src="../assets/sheep.jpeg">
    <WebsiteDescription msg="Training AI User Interface."/>
  </div>
</template>

<script>
// @ is an alias to /src
import WebsiteDescription from '@/components/WebsiteDescription.vue'

export default {
  name: 'HomeView',
  components: {
    WebsiteDescription
  }
}
</script>
<style scoped>
.logo {
  height: 15em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #1bae60aa);
}
</style>

