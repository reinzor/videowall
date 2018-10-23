import Vue from "vue"

Vue.filter("hoursMinutesSeconds", function(value) {
  let hours =  parseInt(Math.floor(value / 3600)); 
  let minutes = parseInt(Math.floor((value - (hours * 3600)) / 60)); 
  let seconds= parseInt((value - ((hours * 3600) + (minutes * 60))) % 60); 

  let dHours = (hours > 9 ? hours : '0' + hours);
  let dMins = (minutes > 9 ? minutes : '0' + minutes);
  let dSecs = (seconds > 9 ? seconds : '0' + seconds);

  return dHours + ":" + dMins + ":" + dSecs;
})