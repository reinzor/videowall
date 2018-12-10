<template>
  <div id="videoWall">
    <ScreenGrid :playerState="playerState" />
  </div>
</template>

<script>
import ScreenGrid from './ScreenGrid.vue'

export default {
  name: 'Player',
  components: {
    ScreenGrid
  },
  created () {
    this.$options.sockets.onmessage = (data) => this.messageReceived(data)
    this.$options.sockets.onopen = (data) => this.newConnection(data)
  },
  data () {
    return {
      playerState: {}
    }
  },
  methods: {
    newConnection (data) {
      console.log(data)
    },
    messageReceived (data) {
      this.playerState = JSON.parse(data.data)
    }
  }
}
</script>

<style>
#videoWall {
  padding-top: 20px;
}
</style>
