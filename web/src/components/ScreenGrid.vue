<template>
  <b-card id="screenGrid" class="mx-auto"
          :style="{width: `${screenGrid.w}px`}">
    <div slot="header">
      <b-button-toolbar class="float-sm-right" size="sm" >
        <b-button-group v-if="editState.active" class="mx-1">
          <b-button variant="outline-secondary" @click="cancelEdit"><v-icon name="times" /></b-button>
          <b-button variant="outline-secondary" @click="applyEdit"><v-icon name="check" /></b-button>
        </b-button-group>
        <b-button v-else variant="outline-secondary" @click="edit"><v-icon name="edit" /></b-button>
      </b-button-toolbar>
    </div>
    <div id="screenGridLayout" v-on:click="screenGridLayoutClicked($event)">
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
                  <b-button variant="outline-secondary"><v-icon name="plug" /></b-button>
                  <b-button variant="outline-secondary" v-if="editState.active"><v-icon name="edit" /></b-button>
                  <b-button variant="outline-secondary" @click="removeScreen(screen.i)" v-if="editState.active"><v-icon name="times" /></b-button>
                </b-button-group>
              </b-button-toolbar>
            </div>
          </b-card>
        </grid-item>
      </grid-layout>
    </div>
    <div slot="footer">
      <PlayerBar />
    </div>
  </b-card>
</template>

<script>
import VueGridLayout from 'vue-grid-layout';
import PlayerBar from './PlayerBar.vue';

export default {
  name: 'ScreenGrid',
  components: {
    PlayerBar
  },
  data () {
    return {
      editState: {
        active: false,
        screensBeforeEdit: null
      },
      screenGrid: {
        w: 1280,
        h: 720
      },
      screens: [
        {"x":0,"y":0,"w":200,"h":157,"i":"0"},
        {"x":2,"y":0,"w":200,"h":157,"i":"1"}
      ]
    }
  },
  methods: {
    edit () {
      this.editState.screensBeforeEdit = JSON.parse(JSON.stringify(this.screens))
      this.editState.active = true
    },
    cancelEdit () {
      this.screens = this.editState.screensBeforeEdit
      this.editState.active = false
    },
    applyEdit () {
      this.editState.active = false
    },
    addScreen (x, y) {
      this.screens.push({
        x: x,
        y: y,
        w: 200,
        h: 200,
        i: this.screens.length
      })
    },
    removeScreen (i) {
      this.screens = this.screens.filter((s) => {
        return s.i !== i;
      });
    },
    screenGridLayoutClicked (e) {
      if (this.editState.active && e.target.getAttribute('class') == 'vue-grid-layout') {
        this.addScreen(e.offsetX, e.offsetY)
      }
    }
  }
}
</script>
<style>
  #screenGrid > .card-body {
    padding: 0;
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
</style>
