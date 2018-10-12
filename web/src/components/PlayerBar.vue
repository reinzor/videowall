<template>
  <div id="playerBar">
    <PlaylistModal />
    <b-button-group>
      <b-button variant="outline-secondary"><v-icon name="backward" /></b-button>
      <b-button variant="outline-secondary"><v-icon name="play" /></b-button>
      <b-button variant="outline-secondary"><v-icon name="forward" /></b-button>
    </b-button-group>
    <b-progress :max="100">
      <b-progress-bar :value="66">
        Awesome
      </b-progress-bar>
    </b-progress>
    <b-button-group>
      <b-button variant="outline-secondary"  v-b-modal.playlistModal><v-icon name="list-ul" /></b-button>
    </b-button-group>
  </div>
</template>

<script>
import PlaylistModal from './PlaylistModal.vue';

export default {
  name: 'PlayerBar',
  components: {
    PlaylistModal
  }
}
</script>
<style>
#playerBar .btn-group {
  margin-left: 5px;
}
#playerBar .progress {
  display: inline-block;
  width: 400px;
  margin-left: 5px;
}
#playerBar .progress-bar {
  display: inline-block;
}
</style>
