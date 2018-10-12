<template>
  <div id="videoWall">
    <ScreenGrid />
  </div>
</template>

<script>
import ScreenGrid from './ScreenGrid.vue'

export default {
  name: 'Player',
  components: {
    ScreenGrid
  }
}
</script>

<style>
#videoWall {
  padding-top: 20px;
}
</style>
