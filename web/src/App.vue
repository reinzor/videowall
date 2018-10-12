<template>
  <div id="app">
    <NavBar />
    <Player />
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue'
import Player from './components/Player.vue'

export default {
  name: 'app',
  components: {
    NavBar,
    Player
  }
}
</script>

<style> 
</style>
