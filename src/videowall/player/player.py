import logging
import os.path
import sys
import threading
import time

from videowall.gi_version import GLib, Gst, GObject, Gdk, Gtk
from videowall.networking.message_definition import VideocropConfig

from .player_exceptions import PlayerException
from .player_platforms import PlayerPlatform, PlayerPlatformPC, PlayerPlatformRaspberryPi, get_player_platforms

logger = logging.getLogger(__name__)


class Player(object):
    Gst.init(None)
    GObject.threads_init()

    def __init__(self, platform, name="Player", time_overlay=False, text_overlay=''):
        if not issubclass(platform, PlayerPlatform):
            raise PlayerException("Invalid player platform {}, available platforms: {}".format(platform,
                                                                                               get_player_platforms()))

        screen = Gdk.Screen.get_default()
        self._screen_width = screen.get_width()
        self._screen_height = screen.get_height()

        self._platform = platform
        self._g_pipeline = None
        self._state = Gst.State.NULL
        self._position = 0
        self._duration = 0
        self._filename = None
        self._g_timer_callback_interval = 100
        self._wait_for_state_interval = 0.1
        self._wait_for_state_max_duration = 5
        self._time_overlay = time_overlay
        self._text_overlay = text_overlay + ' | {}x{}'.format(self._screen_width, self._screen_height)

        GLib.timeout_add(self._g_timer_callback_interval, self._g_timer_callback)

        # Set-up window
        self._window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self._window.set_title(name)
        self._window.set_default_size(self._screen_width, self._screen_height)
        self._movie_view = Gtk.DrawingArea()
        self._window.add(self._movie_view)
        self._window.show_all()

        def run_player_thread():
            Gtk.main()

        self._gobject_thread = threading.Thread(target=run_player_thread)
        self._gobject_thread.start()

        logger.info("Player constructed for window (%dx%d)", self._screen_width, self._screen_height)

    def _g_timer_callback(self):
        if self._g_pipeline and self._state == Gst.State.PLAYING:
            _, self._duration = self._g_pipeline.query_duration(Gst.Format.TIME)
            _, self._position = self._g_pipeline.query_position(Gst.Format.TIME)
        else:
            self._duration = 0
            self._position = 0

        GLib.timeout_add(self._g_timer_callback_interval, self._g_timer_callback)

    def _g_construct_pipeline(self, filename, videocrop_config):
        real_path = os.path.realpath(os.path.expanduser(filename))

        if os.environ.get('DISPLAY') is None:
            raise PlayerException("No $DISPLAY environment variable is set, the ximagesink will not work")

        launch_cmd = ""
        if os.path.isfile(real_path):
            launch_cmd += "filesrc location={}".format(real_path)

            if self._platform == PlayerPlatformPC:
                launch_cmd += " ! decodebin"
            elif self._platform == PlayerPlatformRaspberryPi:
                launch_cmd += " ! qtdemux ! h264parse ! omxh264dec"

            launch_cmd += " ! videocrop bottom={} left={} right={} top={}".format(videocrop_config.bottom,
                                                                                  videocrop_config.left,
                                                                                  videocrop_config.right,
                                                                                  videocrop_config.top)
            launch_cmd += " ! videoconvert"
            if self._text_overlay:
                launch_cmd += ' ! textoverlay text="{}"'.format(self._text_overlay)
            if self._time_overlay:
                launch_cmd += " ! timeoverlay"
            launch_cmd += "! queue"

            logger.debug("Creating pipeline from launch command %s ..", launch_cmd)
        else:
            error_image_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets", "error.jpg")
            launch_cmd += "filesrc location={}".format(error_image_location)
            launch_cmd += " ! jpegparse ! jpegdec ! imagefreeze"
            if self._text_overlay:
                launch_cmd += ' ! textoverlay text="{}\n{}"'.format("%s not found" % filename, self._text_overlay)
            launch_cmd += " ! videoconvert"

        launch_cmd += " ! ximagesink"   # or ! fakesink sync=true # sync required for realtime playback

        logger.debug("gst-launch-1.0 -v %s", launch_cmd)
        self._g_pipeline = Gst.parse_launch(launch_cmd)
        self._filename = filename

        sink = self._g_pipeline.get_child_by_index(0)
        sink.set_window_handle(self._movie_view.get_property('window').get_xid())

        self._g_pipeline.get_bus().connect("message", self._g_on_bus_msg)
        self._g_pipeline.get_bus().add_signal_watch()
        self._g_set_pipeline_state(Gst.State.PLAYING)

    def _g_destroy_pipeline(self):
        if self._g_pipeline is not None:
            self._g_set_pipeline_state(Gst.State.NULL)
            self._g_pipeline = None
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
        self._g_pipeline.set_state(state)

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

        if state == Gst.State.PLAYING:
            while self._duration == 0:
                dt = time.time() - t_start
                if dt > self._wait_for_state_max_duration:
                    logger.fatal("Duration was not set within %.2f seconds!", self._wait_for_state_max_duration)
                    sys.exit(1)
                logger.warn("[%.2f/%.2f] Waiting for duration to be set", dt, self._wait_for_state_max_duration)
                time.sleep(self._wait_for_state_interval)

    def close(self):
        Gtk.main_quit()
        logger.info("Waiting for the GTK Thread to join ..")
        self._gobject_thread.join()

    def get_position(self):
        return self._position

    def get_position_seconds(self):
        return round(self.get_position() / 1e9, 2)

    def get_duration(self):
        if self._duration == 0:
            raise PlayerException("Please call play first!")
        return self._duration

    def get_duration_seconds(self):
        return round(self.get_duration() / 1e9, 2)

    def get_filename(self):
        if self._filename is None:
            raise PlayerException("No filename available, please first play a file")
        return self._filename

    def play(self, filename, videocrop_config=VideocropConfig(0, 0, 0, 0)):
        self.stop()

        GLib.idle_add(self._g_construct_pipeline, filename, videocrop_config)
        self._wait_for_state(Gst.State.PLAYING)

    def pause(self):
        GLib.idle_add(self._g_set_pipeline_state, Gst.State.PAUSED)
        self._wait_for_state(Gst.State.PAUSED)

    def resume(self):
        GLib.idle_add(self._g_set_pipeline_state, Gst.State.PLAYING)
        self._wait_for_state(Gst.State.PLAYING)

    def stop(self):
        GLib.idle_add(self._g_destroy_pipeline)
        self._wait_for_state(Gst.State.NULL)

    def is_playing(self):
        return self._state == Gst.State.PLAYING
