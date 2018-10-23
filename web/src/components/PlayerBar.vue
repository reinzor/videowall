<template>
  <div id="playerBar">
    <PlaylistModal />
    <b-button-group>
      <b-button variant="outline-secondary"><v-icon name="backward" /></b-button>
      <b-button variant="outline-secondary"><v-icon name="play" /></b-button>
      <b-button variant="outline-secondary"><v-icon name="forward" /></b-button>
    </b-button-group>
    <div class="playerTime">
      <b-form-input type="text" :placeholder="position | hoursMinutesSeconds" disabled />
    </div>
    <div id="playerProgress">
      <b-progress :max="currentVideo.duration" variant="info">
        <b-progress-bar :value="position" v-text="currentVideo.filename" />
      </b-progress>
    </div>
    <div class="playerTime">
      <b-form-input type="text" :placeholder="currentVideo.duration | hoursMinutesSeconds" disabled />
    </div>
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
  },
  data () {
    return {
      currentVideo: {
        filename: 'big_buck_bunny_720p_30mb.mp4',
        duration: 460,
        width: 1280,
        height: 720
      },
      position: 30
    }
  }
}
</script>
<style>
#playerBar .btn-group {
  margin: 5px;
}

#playerProgress {
  display: inline-block;
  width: 884px;
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
