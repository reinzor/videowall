import Vue from 'vue'

import BootstrapVue from 'bootstrap-vue'
Vue.use(BootstrapVue);
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

import Icon from 'vue-awesome/components/Icon'
import 'vue-awesome/icons'
Vue.component('v-icon', Icon)

import VueSocketio from 'vue-socket.io';
Vue.use(VueSocketio, 'http://localhost:3000');

import App from './App.vue'

Vue.config.productionTip = false

new Vue({
  render: h => h(App)
}).$mount('#app')
