<template>
  <div id="app">
    <ScreenGrid />
  </div>
</template>

<script>
import ScreenGrid from './components/ScreenGrid.vue'

export default {
  name: 'app',
  components: {
    ScreenGrid
  },
  mounted () {
    this.$socket.emit('test', {
      banana: 'omg'
    });
  },
  sockets:{
    connect: function(){
      console.log('socket connected')
    },
    customEmit: function(val){
      console.log('this method was fired by the socket server. eg: io.emit("customEmit", data)')
    }
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
