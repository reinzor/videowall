<template>
  <b-card id="screenGrid" class="mx-auto"
          :style="{width: `${screenGrid.w}px`}">
    <div slot="header">
      <b-button-toolbar class="float-sm-right" size="sm" >
        <b-button variant="outline-secondary" v-b-modal.clientsModal style="margin-right: 5px"><v-icon name="users" /></b-button>
        <b-button-group v-if="editState.active" class="mx-1">
          <b-button variant="outline-secondary" @click="cancelEdit"><v-icon name="times" /></b-button>
          <b-button variant="outline-secondary" @click="applyEdit"><v-icon name="check" /></b-button>
        </b-button-group>
        <b-button v-else variant="outline-secondary" @click="edit"><v-icon name="edit" /></b-button>
      </b-button-toolbar>
    </div>
    <div id="screenGridLayout" v-on:click="screenGridLayoutClicked($event)">
      <b-modal id="clientsModal" hide-footer title="Clients">
        <b-list-group>
          <b-button @click="syncMedia">Sync media</b-button>
          <b-list-group-item v-for="client in clients" class="flex-column align-items-start" :key="client.ip" :variant="clientActive(client.ip) ? 'success' : 'danger'">
            <div>
              <div class="d-flex justify-content-between align-items-center">
                <table class="clientTable">
                  <tr><td>IP:</td><td v-text="client.ip"></td></tr>
                  <tr><td>Username:</td><td v-text="client.username"></td></tr>
                  <tr><td>Media path:</td><td v-text="client.media_path"></td></tr>
                </table>
                <b-badge variant="info">Age: {{client.age}}</b-badge>
              </div>
            </div>
          </b-list-group-item>
        </b-list-group>
      </b-modal>
      <b-modal ref="addModal" hide-footer title="Add screen for client">
        <div class="d-block text-center">
          <b-form @submit.prevent="addScreen()">
            <b-form-select :options="clientIpOptions" required v-model="editState.addScreenIp">
            </b-form-select>
            <b-button type="submit" variant="primary">Add screen</b-button>
          </b-form>
        </div>
      </b-modal>
      <grid-layout :style="{height: `${screenGrid.h}px`, cursor: editState.active ? 'cell' : 'default'}"
                   :layout="screens"
                   :colNum="1280"
                   :rowHeight="1"
                   :maxRows="720"
                   :isDraggable="editState.active"
                   :isResizable="editState.active"
                   :isMirrored="false"
                   :margin="[0, 0]"
                   :verticalCompact="false"
                   :autoSize="true"
                   :useCssTransforms="true">
        <grid-item v-for="screen in screens"
                   :key="screen.i"
                   class="screen"
                   :style="{cursor: editState.active ? 'grabbing' : 'default'}"
                   :x="screen.x"
                   :y="screen.y"
                   :w="screen.w"
                   :h="screen.h"
                   :i="screen.i">
          <b-card :footer="`${screen.x},${screen.y} [${screen.w}x${screen.h}]`">
            <div slot="header">
              <span v-text="`Screen ${screen.i}`" />
              <b-button-toolbar class="float-sm-right">
                <b-button-group class="mx-1" size="sm">
                  <b-button :variant="clientActive(screen.i) ? 'success': 'danger'"><v-icon name="plug" /></b-button>
                  <b-button variant="danger" @click="removeScreen(screen.i)" v-if="editState.active"><v-icon name="trash-alt" /></b-button>
                </b-button-group>
              </b-button-toolbar>
            </div>
          </b-card>
        </grid-item>
      </grid-layout>
    </div>
  </b-card>
</template>

<script>
import VueGridLayout from 'vue-grid-layout';

export default {
  name: 'ScreenGrid',
  components: {
    VueGridLayout
  },
  props: {
    clientConfig: {
      type: Object,
      required: true
    },
    clients: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      editState: {
        active: false,
        addScreenIp: '',
        clickedPosition: {
          x: 0,
          y: 0
        }
      },
      screenGrid: {
        w: 1280,
        h: 720
      },
      screens: []
    }
  },
  watch: {
    clientConfig: function (clientConfig) {
      if (!this.editState.active) {
        this.screens = []
        for (var ip in clientConfig) {
          this.screens.push({
            i: ip,
            x: clientConfig[ip].videocrop_config.left,
            y: clientConfig[ip].videocrop_config.top,
            w: 1280 - clientConfig[ip].videocrop_config.left - clientConfig[ip].videocrop_config.right,
            h: 720 - clientConfig[ip].videocrop_config.top - clientConfig[ip].videocrop_config.bottom
          })
        }
      }
    }
  },
  computed: {
    clientIpOptions () {
      var clientIpOptions = []
      this.clients.forEach((client) => {
        if (!(client.ip in this.clientConfig)) {
          clientIpOptions.push(client.ip)
        }
      })
      return clientIpOptions
    }
  },
  methods: {
    edit () {
      this.editState.active = true
    },
    cancelEdit () {
      this.editState.active = false
    },
    applyEdit () {
      var clientConfig = {}
      this.screens.forEach((screen) => {
        clientConfig[screen.i] = {
          videocrop_config: {
            bottom: 720 - screen.y - screen.h,
            left: screen.x,
            right: 1280 - screen.x - screen.w,
            top: screen.y
          }
        }
      })
      this.$socket.sendObj({
        command: 'set_client_config',
        arguments: {
          config: clientConfig
        }
      })
      this.editState.active = false
    },
    addScreen () {
      this.screens.push({
        x: this.editState.clickedPosition.x,
        y: this.editState.clickedPosition.y,
        w: 200,
        h: 200,
        i: this.editState.addScreenIp
      })
      this.$refs.addModal.hide()
    },
    removeScreen (i) {
      this.screens = this.screens.filter((s) => {
        return s.i !== i;
      });
    },
    screenGridLayoutClicked (e) {
      if (this.editState.active && e.target.getAttribute('class') == 'vue-grid-layout') {
        this.$refs.addModal.show()
        this.editState.clickedPosition.x = e.offsetX
        this.editState.clickedPosition.y = e.offsetY
      }
    },
    clientActive (ip) {
      var active = false
      this.clients.forEach((client) => {
        if (client.ip == ip) {
          if (client.age < 5) {
            active = true
          }
        }
      })
      return active
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
  #screenGrid > .card-body {
    padding: 0;
  }
  #screenGrid > .card-header {
    padding: 5px;
  }
  #screenGridLayout {
    background-image: url("../assets/bigbunny.jpg");
    background-repeat: repeat-y;
  }
  .screen .card {
    background: none;
    height: 100%;
    border: 1px solid rgba(255, 255, 255, 0.8)
  }
  .screen .card-header {
    background-color: rgba(255, 255, 255, 0.5);
    font-size: 10px;
    color: grey;
    padding: 0;
  }
  .screen .card-header div {
    padding: 0px !important;
    margin: 0px !important;
  }
  .screen .card-header button {
    padding: 0 5px;
  }
  .screen .card-header span {
    margin: 3px;
    line-height: 23px;
  }
  .screen .card-footer {
    background-color: rgba(255, 255, 255, 0.5);
  }
  .screen .card-footer {
    font-size: 10px;
    color: grey;
    padding: 4px 3px;
  }
  .clientTable {
    font-size: 10px;
  }
</style>
