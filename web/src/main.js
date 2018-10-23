import Vue from 'vue'

import VueRouter from 'vue-router'
Vue.use(VueRouter)

import BootstrapVue from 'bootstrap-vue'
Vue.use(BootstrapVue);
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

import Icon from 'vue-awesome/components/Icon'
import 'vue-awesome/icons'
Vue.component('v-icon', Icon)

import VueSocketio from 'vue-socket.io';
Vue.use(VueSocketio, 'http://localhost:3000');

import "./filters"

import App from './App.vue'
import Player from './components/Player.vue'

Vue.config.productionTip = false

const routes = [
  { path: '/', component: Player }	
]

const router = new VueRouter({
  routes
})

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
