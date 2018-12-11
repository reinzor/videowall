<template>
  <div id="playerBar">
    <PlaylistModal :playerState="playerState" @play="$emit('play', $event)" />
    <b-button-group>
      <b-button variant="outline-secondary"><v-icon name="backward" /></b-button>
      <b-button variant="outline-secondary" v-on:click="$emit('play', playerState.current_media_filename)" :disabled="!playerState.current_media_filename">
        <v-icon name="sync-alt" />
      </b-button>
      <b-button variant="outline-secondary"><v-icon name="forward" /></b-button>
    </b-button-group>
    <div class="playerTime">
      <b-form-input type="text" :placeholder="playerState.position | hoursMinutesSeconds" disabled />
    </div>
    <div id="playerProgress">
      <b-progress :max="playerState.duration" variant="info">
        <b-progress-bar :value="playerState.position" v-text="playerState.current_media_filename" />
      </b-progress>
    </div>
    <div class="playerTime">
      <b-form-input type="text" :placeholder="playerState.duration | hoursMinutesSeconds" disabled />
    </div>
    <b-button-group>
      <b-button variant="outline-secondary" v-b-modal.playlistModal><v-icon name="list-ul" /></b-button>
    </b-button-group>
  </div>
</template>

<script>
import PlaylistModal from './PlaylistModal.vue';

export default {
  name: 'PlayerBar',
  components: {
    PlaylistModal
  },
  props: {
    playerState: {
      type: Object,
      required: true
    }
  }
}
</script>
<style>
#playerBar {
  background-color: rgba(0, 0, 0, 0.03);
  border-left: 1px solid rgba(0, 0, 0, 0.125);
  border-right: 1px solid rgba(0, 0, 0, 0.125);
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
  width: 1280px;
}
#playerBar .btn-group {
  margin: 5px;
}

#playerProgress {
  display: inline-block;
  width: 882px;
}
#playerProgress .progress {
  height: 38px;
  margin: 5px;
  text-align: center;
}
#playerProgress .progress-bar {
  padding: 15px;
}
#playerDuration {
  display: inline-block;
  width: 100px;
  margin: 5px;
}
.playerTime {
  display: inline-block;
  width: 90px;
  margin: 5px;
}
</style>
