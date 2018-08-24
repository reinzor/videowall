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

    def __init__(self, platform, show_gui=True):
        if not issubclass(platform, PlayerPlatform):
            raise PlayerException("Invalid player platform {}, available platforms: {}".format(platform,
                                                                                               get_player_platforms()))

        self._platform = platform
        self._show_gui = show_gui
        self._pipeline = None

        def run_player_thread():
            GObject.MainLoop().run()

        self._gobject_thread = threading.Thread(target=run_player_thread)
        self._gobject_thread.start()

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

    def play(self, filename, videocrop_config=VideocropConfig(0, 0, 0, 0)):
        if self._pipeline:
            self.stop()

        real_path = os.path.realpath(os.path.expanduser(filename))
        if not os.path.isfile(real_path):
            raise PlayerException("File '{}' does not exist!".format(filename))

        self._pipeline = self._get_pipeline(filename, self._platform, self._show_gui, videocrop_config)
        self._set_pipeline_state(Gst.State.PLAYING)

        self._pipeline.get_bus().connect("message", self._on_bus_msg)
        self._pipeline.get_bus().add_signal_watch()

        # Wait until the video is loaded
        # TODO: Is there an other 
        while self.get_duration() == 0:
            time.sleep(0.1)

    def stop(self):
        self._set_pipeline_state(Gst.State.NULL)

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
