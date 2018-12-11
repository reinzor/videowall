<template>
  <div id="videoWall">
    <ScreenGrid :clientConfig="serverState.client_config" :clients="serverState.clients" />
    <center>
      <PlayerBar :playerState="serverState.player" @play="play($event)" />
    </center>
  </div>
</template>

<script>
import PlayerBar from './PlayerBar.vue';
import ScreenGrid from './ScreenGrid.vue'

export default {
  name: 'Player',
  components: {
    PlayerBar,
    ScreenGrid
  },
  created () {
    this.$options.sockets.onmessage = (data) => this.messageReceived(data)
    this.$options.sockets.onopen = (data) => this.newConnection(data)
  },
  data () {
    return {
      serverState: {
        client_config: {},
        clients: [],
        player: {}
      }
    }
  },
  methods: {
    newConnection (data) {
      console.log(data)
    },
    messageReceived (data) {
      this.serverState = JSON.parse(data.data)
    },
    play(filename) {
      this.$socket.sendObj({
        command: 'play',
        arguments: {
          filename: filename
        }
      })
    }
  }
}
</script>

<style>
#videoWall {
  padding-top: 20px;
}
</style>
