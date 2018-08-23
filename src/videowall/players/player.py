import logging
import os.path
import socket
import threading
import time

from videowall.gi_version import Gst, GObject
from videowall.networking.message_definition import VideocropConfig

from .player_exceptions import PlayerException
from .player_platforms import PlayerPlatform, PlayerPlatformX86, PlayerPlatformRaspberryPi, get_player_platforms

logger = logging.getLogger(__name__)


class Player(object):
    Gst.init(None)

    def __init__(self, platform, filename, ip, clock_port,
                 show_gui=True,
                 seek_grace_time=0,
                 seek_lookahead=0,
                 videocrop_config=VideocropConfig(0, 0, 0, 0)):
        if not issubclass(platform, PlayerPlatform):
            raise PlayerException("Invalid player platform {}, available platforms: {}".format(platform,
                                                                                               get_player_platforms()))

        real_path = os.path.realpath(os.path.expanduser(filename))
        if not os.path.isfile(real_path):
            raise PlayerException("File '{}' does not exist!".format(filename))

        try:
            socket.inet_pton(socket.AF_INET, ip)
        except socket.error as e:
            raise PlayerException(e)

        if not isinstance(clock_port, int):
            raise PlayerException("Port should be an integer, current value: {}".format(clock_port))

        if not isinstance(show_gui, bool):
            raise PlayerException("GUI should be a boolean")

        if not any([isinstance(seek_grace_time, t) for t in (int, long)]):
            raise PlayerException("Seek grace time should be an integer, current value: {}".format(seek_grace_time))

        if not any([isinstance(seek_lookahead, t) for t in (int, long)]):
            raise PlayerException("Seek lookahead should be an integer, current value: {}".format(seek_lookahead))

        self._player_platform = platform
        self._filename = filename
        self._ip = ip
        self._port = clock_port
        self._base_time = None
        self._seek_grace_time = seek_grace_time
        self._seek_lookahead = seek_lookahead
        self._pipeline = self._get_pipeline(filename, platform, show_gui, videocrop_config)
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
    def _get_pipeline(filename, player_platform, gui, videocrop_config):
        launch_cmd = "filesrc location={}".format(filename)

        if player_platform == PlayerPlatformX86:
            launch_cmd += " ! decodebin"
        elif player_platform == PlayerPlatformRaspberryPi:
            launch_cmd += " ! qtdemux ! h264parse ! omxh264dec"

        gui = True  # TODO: Remove, first get GTK to work properly
        if gui:
            if os.environ.get('DISPLAY') is None:
                raise PlayerException("No $DISPLAY environment variable is set, the ximagesink will not work")

            launch_cmd += " ! videocrop bottom={} left={} right={} top={}".format(videocrop_config.bottom,
                                                                                  videocrop_config.left,
                                                                                  videocrop_config.right,
                                                                                  videocrop_config.top)
            launch_cmd += " ! videoconvert ! queue ! ximagesink"
        else:
            launch_cmd += " ! fakesink"

        logger.debug("Creating pipeline from launch command %s ..", launch_cmd)

        pipeline = Gst.parse_launch(launch_cmd)
        return pipeline

    def _eos_callback(self, bus, msg):
        pass

    def _on_bus_msg(self, bus, msg):
        if msg is not None:
            if msg.type is Gst.MessageType.EOS:
                logger.info("Gst.MessageType.EOS")
                self._eos_callback(bus, msg)

    def _set_pipeline_state(self, state):
        logger.info("Setting the pipeline state to %s", state)
        self._pipeline.set_state(state)

    def _get_updated_seek_time(self, seek_time):
        if not any([isinstance(seek_time, t) for t in (int, long)]):
            raise PlayerException("Seek time should be an integer, current value: {}".format(seek_time))

        while self.get_duration() == 0:
            time.sleep(0.1)  # TODO: Can't we use an other call to wait for the pipeline?

        if seek_time < 0 or seek_time > self.get_duration():
            raise PlayerException("Invalid seek_time {}. The value should be between {} and {}",
                                  seek_time, 0, self.get_duration())

        return min(self.get_duration(), seek_time + self._seek_lookahead)

    def _set_base_time(self, base_time, seek_time):
        if not any([isinstance(base_time, t) for t in (int, long)]):
            raise PlayerException("Base time should be an integer, current value: {}".format(base_time))

        logger.info("Setting base time to %d", base_time)
        self._base_time = base_time
        self._pipeline.set_start_time(Gst.CLOCK_TIME_NONE)
        self._pipeline.set_base_time(base_time + seek_time)  # TODO: Figure out why this works

    def _seek(self, seek_time):
        logger.info("Seeking to %d", seek_time)
        self._pipeline.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE, seek_time)

    def play(self, base_time, seek_time):
        updated_seek_time = self._get_updated_seek_time(seek_time)

        self._seek(updated_seek_time)
        self._set_base_time(base_time, updated_seek_time)

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
