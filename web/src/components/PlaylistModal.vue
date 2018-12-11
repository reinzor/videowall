<template>
  <b-modal id="playlistModal" hide-footer title="Playlist">
    <b-list-group>
      <b-list-group-item v-for="media_filename in playerState.media_filenames"
                         class="flex-column align-items-start"
                         :key="media_filename"
                         :variant="playerState.current_media_filename == media_filename ? 'info' : ''">
        <div>
          <div class="d-flex w-100 justify-content-between">
            <h5 class="mb-1" v-text="media_filename"></h5>
            <b-button-group size="sm" class="playlistVideoButtons">
              <b-button variant="outline-secondary" v-on:click="$emit('play', media_filename)">
                <v-icon name="play" v-if="playerState.current_media_filename != media_filename"/>
                <v-icon name="sync-alt" v-else/>
              </b-button>
              <b-button variant="outline-secondary" v-if="playerState.current_media_filename != media_filename" v-on:click="deleteMedia(media_filename)">
                <v-icon name="times" />
              </b-button>
            </b-button-group>
          </div>
        </div>
      </b-list-group-item>
    </b-list-group>
    <b-alert v-if="err" variant="danger" v-text="err" show dismissible />
    <vue2-dropzone ref="dropzone" id="dropzone" :options="dropzoneOptions"
                   @vdropzone-file-added="err = ''"
                   @vdropzone-complete="uploadComplete($refs.dropzone)"
                   @vdropzone-error="uploadError"></vue2-dropzone>
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
    props: {
      playerState: {
        type: Object,
        required: true
      }
    },
    data () {
      return {
        dropzoneOptions: {
          url: '/upload',
          thumbnailWidth: 200,
          maxFilesize: 500
        },
        err: ''
      }
    },
    methods: {
      uploadComplete(dropzone) {
        dropzone.removeAllFiles()
        this.syncMedia()
      },
      uploadError(err) {
        this.err = JSON.parse(err.xhr.response).reason
      },
      deleteMedia(filename) {
        this.$socket.sendObj({
          command: 'delete',
          arguments: {
            filename: filename
          }
        })
        this.syncMedia()
      },
      syncMedia () {
        this.$socket.sendObj({
          command: 'sync_media',
          arguments: {}
        })
      }
    }
  }
</script>

<style>
#playlistModal .list-group-item {
  padding: 10px;
  /*cursor: move;*/
}
.playlistVideoButtons {
  margin: 0 !important;
  padding: 0 !important;
}
.playlistVideoButtons button {
  padding: 0 5px !important;
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
