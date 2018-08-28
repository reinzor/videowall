import logging
import os.path
import sys
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
        self._state = Gst.State.NULL
        self._position = 0
        self._duration = 0
        self._g_timer_callback_interval = 100
        self._wait_for_state_interval = 0.1
        self._wait_for_state_max_duration = 0

        GLib.timeout_add(self._g_timer_callback_interval, self._g_timer_callback)

        def run_player_thread():
            GObject.MainLoop().run()

        self._gobject_thread = threading.Thread(target=run_player_thread)
        self._gobject_thread.start()

        logger.debug("Player constructed")

    def _g_timer_callback(self):
        if self._pipeline and self._state == Gst.State.PLAYING:
            _, self._duration = self._pipeline.query_duration(Gst.Format.TIME)
            _, self._position = self._pipeline.query_position(Gst.Format.TIME)
        else:
            self._duration = 0
            self._position = 0

        GLib.timeout_add(self._g_timer_callback_interval, self._g_timer_callback)

    def _g_construct_pipeline(self, filename, videocrop_config):
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

        self._pipeline.get_bus().connect("message", self._g_on_bus_msg)
        self._pipeline.get_bus().add_signal_watch()
        self._g_set_pipeline_state(Gst.State.PLAYING)

    def _g_destroy_pipeline(self):
        if self._pipeline is not None:
            self._g_set_pipeline_state(Gst.State.NULL)
            self._pipeline = None
            self._state = Gst.State.NULL

    def _g_on_bus_msg(self, bus, msg):
        if msg is not None:
            if msg.type is Gst.MessageType.STATE_CHANGED:
                _, newstate, _ = msg.parse_state_changed()
                if self._state != newstate:
                    self._state = newstate
                    logger.debug("Pipeline state changed to %s ... ", self._state)
            if msg.type is Gst.MessageType.EOS:
                self._g_destroy_pipeline()

    def _g_set_pipeline_state(self, state):
        logger.info("Setting the pipeline state to %s ... ", state)
        self._pipeline.set_state(state)

    def _wait_for_state(self, state):
        t_start = time.time()

        time.sleep(self._wait_for_state_interval)
        while self._state != state:
            dt = time.time() - t_start
            if dt > self._wait_for_state_max_duration:
                logger.fatal("Transition to state %s took too long: Timeout of %.2f seconds exceeded!", state,
                             self._wait_for_state_max_duration)
                sys.exit(1)
            logger.warn("[%.2f/%.2f] Waiting for state transition to %s", dt, self._wait_for_state_max_duration, state)
            time.sleep(self._wait_for_state_interval)

    def get_position(self):
        return self._position

    def get_duration(self):
        return self._duration

    def play(self, filename, videocrop_config=VideocropConfig(0, 0, 0, 0)):
        self.stop()

        GLib.idle_add(self._g_construct_pipeline, filename, videocrop_config)
        self._wait_for_state(Gst.State.PLAYING)

    def stop(self):
        GLib.idle_add(self._g_destroy_pipeline)
        self._wait_for_state(Gst.State.NULL)
