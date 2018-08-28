import logging
import os.path
import socket
import threading
import time

from videowall.gi_version import GLib, Gst, GObject
from videowall.networking.message_definition import VideocropConfig

from .player_exceptions import PlayerException
from .player_platforms import PlayerPlatform, PlayerPlatformX86, PlayerPlatformRaspberryPi, get_player_platforms

logger = logging.getLogger(__name__)


class Player(object):
    Gst.init(None)
    GObject.threads_init()

    def __init__(self, platform, show_gui=True):
        if not issubclass(platform, PlayerPlatform):
            raise PlayerException("Invalid player platform {}, available platforms: {}".format(platform,
                                                                                               get_player_platforms()))

        if not isinstance(show_gui, bool):
            raise PlayerException("show_gui should be a boolean")

        self._platform = platform
        self._show_gui = show_gui
        self._pipeline = None

        def run_player_thread():
            GObject.MainLoop().run()

        self._gobject_thread = threading.Thread(target=run_player_thread)
        self._gobject_thread.start()

        logger.debug("Player constructed")

    def _construct_pipeline(self, filename, videocrop_config):
        if self._pipeline:
            self.stop()

        real_path = os.path.realpath(os.path.expanduser(filename))
        if not os.path.isfile(real_path):
            raise PlayerException("File '{}' does not exist!".format(filename))

        launch_cmd = "filesrc location={}".format(filename)

        if self._platform == PlayerPlatformX86:
            launch_cmd += " ! decodebin"
        elif self._platform == PlayerPlatformRaspberryPi:
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

        self._pipeline = Gst.parse_launch(launch_cmd)
    #
    #     self._pipeline.get_bus().connect("message", self._on_bus_msg)
    #     self._pipeline.get_bus().add_signal_watch()
    #     self._set_pipeline_state(Gst.State.READY)
    #
    # def _on_bus_msg(self, bus, msg):
    #     if msg is not None:
    #         if msg.type is Gst.MessageType.EOS:
    #             self.stop()

    def _get_pipeline_state(self):
        _, state, _ = self._pipeline.get_state(Gst.CLOCK_TIME_NONE)
        return state

    def get_position(self):
        _, position = self._pipeline.query_position(Gst.Format.TIME)
        return position

    def get_duration(self):
        _, duration = self._pipeline.query_duration(Gst.Format.TIME)
        return duration

    def _set_pipeline_state(self, state):
        logger.info("Setting the pipeline state to %s ... ", state)
        GLib.idle_add(self._pipeline.set_state, state)

        time.sleep(1)
        # if state == Gst.State.PLAYING:
        #     while self.get_duration() == 0:
        #         time.sleep(0.1)

    def play(self, filename, videocrop_config=VideocropConfig(0, 0, 0, 0)):
        self._construct_pipeline(filename, videocrop_config)
        self._set_pipeline_state(Gst.State.PLAYING)

    def stop(self):
        self._set_pipeline_state(Gst.State.NULL)

    def is_playing(self):
        return self._get_pipeline_state() == Gst.State.PLAYING
