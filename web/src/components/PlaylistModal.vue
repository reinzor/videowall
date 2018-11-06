<template>
  <b-modal id="playlistModal" hide-footer title="Playlist">
    <b-list-group>
      <draggable v-model="playlist">
        <b-list-group-item v-for="video in playlist" 
                           class="flex-column align-items-start"
                           :key="video.filename"
                           :variant="video.playing ? 'info' : ''">
          <div :style="{opacity: video.enabled ? 1.0 : 0.2}">
            <div class="d-flex w-100 justify-content-between">
              <h5 class="mb-1" v-text="video.filename"></h5>
              <b-button-group size="sm" class="playlistVideoButtons">
                <b-button variant="outline-secondary"><v-icon name="times" /></b-button>
                <b-button variant="outline-secondary" v-if="video.enabled"><v-icon name="check-square" /></b-button>
                <b-button variant="outline-secondary" v-if="!video.enabled"><v-icon name="square" /></b-button>
              </b-button-group>
            </div>
            <div class="playlistVideoBadges">
              <b-badge variant="info">Duration: {{video.duration | hoursMinutesSeconds}}</b-badge>
              <b-badge variant="secondary">Dimensions: {{video.width}}x{{video.height}}</b-badge>
            </div>
          </div>
        </b-list-group-item>
      </draggable>
    </b-list-group>
    <vue2-dropzone ref="dropzone" id="dropzone" :options="dropzoneOptions" @vdropzone-complete="uploadComplete($event, $refs.dropzone)"></vue2-dropzone>
  </b-modal>
</template>

<script>
  import { debounce } from "debounce";
  import draggable from 'vuedraggable'
  import vue2Dropzone from 'vue2-dropzone'
  import 'vue2-dropzone/dist/vue2Dropzone.min.css'

  export default {
    components: {
      draggable,
      vue2Dropzone
    },
    data () {
      return {
        playlist: [
        {
          filename: 'big_buck_bunny_720p_30mb.mp4',
          duration: 460,
          width: 1280,
          height: 720,
          enabled: true,
          playing: false
        },
        {
          filename: 'Friends.mp4',
          duration: 460,
          width: 1280,
          height: 720,
          enabled: true,
          playing: true
        },
        {
          filename: 'Banana.mp4',
          duration: 460,
          width: 1280,
          height: 720,
          enabled: true,
          playing: false
        },
        {
          filename: 'Hola.mp4',
          duration: 460,
          width: 1280,
          height: 720,
          enabled: false,
          playing: false
        },
        ],
        dropzoneOptions: {
          url: '/upload',
          thumbnailWidth: 200,
          maxFilesize: 500
        }
      }
    },
    methods: {
      uploadComplete: debounce((e, dropzone) => {
        dropzone.removeAllFiles()
      }, 3000)
    }
  }
</script>

<style>
#playlistModal .list-group-item {
  padding: 10px;
  cursor: move;
}
.playlistVideoButtons {
  margin: 0 !important;
  padding: 0 !important;
}
.playlistVideoButtons button {
  padding: 0 5px !important;
}
.playlistVideoBadges .badge {
  margin-right: 5px;
}
#playlistModal #dropzone {
  padding: 0;
  border: 1px solid rgba(0, 0, 0, 0.125);
  border-radius: 0.25rem;
}
#playlistModal .dropzone {
  margin-top: 10px;
  min-height: 0px; 
}
#playlistModal .dz-message {
  /*margin: 0;*/
}
#playlistModal .dz-details {
  background-color: #17a2b8;
  border-radius: 10px;
}
#playlistModal .dz-image {
  height: 100px;
}
#playlistModal .dz-progress {
  opacity: 0.8;
  margin-top: -2px;
  width: 80px;
  height: 10px;
}
#playlistModal .modal-dialog {
  max-width: 80%;
}
</style>
