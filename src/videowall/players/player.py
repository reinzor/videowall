import logging
import os.path
import socket
import threading
import time

from videowall.gi_version import Gst, GObject

from .player_exceptions import PlayerException
from .player_platforms import PlayerPlatform, PlayerPlatformX86, PlayerPlatformRaspberryPi, get_player_platforms

logger = logging.getLogger(__name__)


class Player(object):
    Gst.init(None)

    def __init__(self, player_platform, filename, ip, port, gui, seek_grace_time, seek_lookahead):
        if not issubclass(player_platform, PlayerPlatform):
            raise PlayerException("Invalid player platform {}, available platforms: {}".format(player_platform,
                                                                                               get_player_platforms()))

        real_path = os.path.realpath(os.path.expanduser(filename))
        if not os.path.isfile(real_path):
            raise PlayerException("File '{}' does not exist!".format(filename))

        try:
            socket.inet_pton(socket.AF_INET, ip)
        except socket.error as e:
            raise PlayerException(e)

        if not isinstance(port, int):
            raise PlayerException("Port should be an integer, current value: {}".format(port))

        if not isinstance(gui, bool):
            raise PlayerException("GUI should be a boolean")

        if not isinstance(seek_grace_time, int):
            raise PlayerException("Seek grace time should be an integer, current value: {}".format(seek_grace_time))

        if not isinstance(seek_lookahead, int):
            raise PlayerException("Seek lookahead should be an integer, current value: {}".format(seek_lookahead))

        self._player_platform = player_platform
        self._filename = filename
        self._ip = ip
        self._port = port
        self._base_time = None
        self._seek_grace_time = seek_grace_time
        self._seek_lookahead = seek_lookahead
        self._pipeline = self._get_pipeline(filename, player_platform, gui)
        self._set_pipeline_state(Gst.State.PAUSED)

        self._bus = self._pipeline.get_bus()
        self._watch_id = self._bus.connect("message", self._on_bus_msg)
        self._bus.add_signal_watch()

        def run_player_thread():
            GObject.MainLoop().run()

        self._player_thread = threading.Thread(target=run_player_thread)
        self._player_thread.start()

        logger.debug("Player constructed")

    @staticmethod
    def _get_pipeline(filename, player_platform, gui):
        launch_cmd = "filesrc location={}".format(filename)

        if player_platform == PlayerPlatformX86:
            launch_cmd += " ! decodebin"
        elif player_platform == PlayerPlatformRaspberryPi:
            launch_cmd += " ! qtdemux ! h264parse ! omxh264dec"

        gui = True  # TODO: Remove, first get GTK to work properly
        if gui:
            if os.environ.get('DISPLAY') is None:
                raise PlayerException("No $DISPLAY environment variable is set, the ximagesink will not work")

            launch_cmd += " ! videoconvert ! queue ! ximagesink"
        else:
            launch_cmd += " ! fakesink"

        logger.debug("Creating pipeline from launch command %s ..", launch_cmd)

        pipeline = Gst.parse_launch(launch_cmd)
        return pipeline

    def _on_bus_msg(self, bus, msg):
        if msg is not None:
            if msg.type is Gst.MessageType.EOS:
                logger.info("Received EOS message, stopping player")
                self.stop()

    def _set_pipeline_state(self, state):
        logger.info("Setting the pipeline state to %s", state)
        self._pipeline.set_state(state)

    def _set_base_time(self, base_time, seek_time):
        if not any([isinstance(base_time, t) for t in (int, long)]):
            raise PlayerException("Base time should be an integer, current value: {}".format(base_time))

        logger.info("Setting base time to %d", base_time)
        self._base_time = base_time
        self._pipeline.set_start_time(Gst.CLOCK_TIME_NONE)
        self._pipeline.set_base_time(base_time + seek_time)  # TODO: Figure out why this works

    def seek(self, seek_time):
        if not any([isinstance(seek_time, t) for t in (int, long)]):
            raise PlayerException("Seek time should be an integer, current value: {}".format(seek_time))

        if seek_time == 0:
            return

        while self.get_duration() == 0:
            time.sleep(0.1)  # TODO: Can't we use an other call to wait for the pipeline?

        if seek_time < 0 or seek_time > self.get_duration():
            raise PlayerException("Invalid seek_time {}. The value should be between {} and {}",
                                  seek_time, 0, self.get_duration())

        delta = self.get_position() - seek_time
        if abs(delta) < self._seek_grace_time:
            logger.info("Skipping seek: abs value of delta %d < sync grace time %d", delta, self._seek_grace_time)
        else:
            corrected_seek_time = min(self.get_duration(), seek_time + self._seek_lookahead)
            logger.info("Seeking to %d (seek_time=%d, seek_lookahead=%d)", corrected_seek_time, seek_time,
                        self._seek_lookahead)
            self._set_pipeline_state(Gst.State.PAUSED)
            self._pipeline.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, seek_time)

    def play(self, base_time, seek_time):
        self._set_base_time(base_time, seek_time)
        self.seek(seek_time)
        self._set_pipeline_state(Gst.State.PLAYING)

    def stop(self):
        self._set_pipeline_state(Gst.State.PAUSED)

    def is_playing(self):
        _, state, _ = self._pipeline.get_state(Gst.CLOCK_TIME_NONE)
        logger.debug("Player state %s", state)
        return state == Gst.State.PLAYING

    def get_filename(self):
        return self._filename

    def get_ip(self):
        return self._ip

    def get_port(self):
        return self._port

    def get_base_time(self):
        return self._base_time

    def get_position(self):
        _, position = self._pipeline.query_position(Gst.Format.TIME)
        return position

    def get_duration(self):
        _, duration = self._pipeline.query_duration(Gst.Format.TIME)
        return duration
