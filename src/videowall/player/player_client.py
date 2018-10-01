from __future__ import print_function

import logging
import os.path
import threading
import time

from videowall.gi_version import GstNet, Gst, Gdk, Gtk
from videowall.util import validate_ip_port

from .player_exceptions import PlayerException
from .player_platforms import PlayerPlatform, PlayerPlatformPC, PlayerPlatformRaspberryPi, get_player_platforms

logger = logging.getLogger(__name__)

ONE_MINUTE_SECONDS = 60


class PlayerClient(object):
    Gst.init(None)

    def __init__(self, platform, clock_ip, clock_port):
        if not issubclass(platform, PlayerPlatform):
            raise PlayerException("Invalid player platform {}, available platforms: {}".format(platform,
                                                                                               get_player_platforms()))
        # Set-up window
        screen = Gdk.Screen.get_default()
        self._screen_width = screen.get_width()
        self._screen_height = screen.get_height()
        self._window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self._window.set_title("PlayerClient")
        self._window.set_default_size(self._screen_width, self._screen_height)
        self._movie_view = Gtk.DrawingArea()
        self._window.add(self._movie_view)
        self._window.show_all()

        validate_ip_port(clock_ip, clock_port)

        clock_name = "clock0"
        try:
            self._clock = GstNet.NetClientClock.new(clock_name, clock_ip, clock_port, 0)
        except TypeError as e:
            raise PlayerException("GstNet.NetClientClock.new({}, {}, {}) failed ({}). Set environment variable "
                                  "GST_DEBUG=1 for more info".format(clock_name, clock_ip, clock_port, e))
        self._pipeline = None

        def run_player_thread():
            Gtk.main()

        self._gobject_thread = threading.Thread(target=run_player_thread)
        self._gobject_thread.start()

        self._platform = platform

        logger.info("Player constructed for window (%dx%d) and clock server (%s:%d)", self._screen_width,
                    self._screen_height, clock_ip, clock_port)

    def _construct_pipeline(self, filename, videocrop_config, text_overlay, time_overlay):
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
            if text_overlay:
                launch_cmd += ' ! textoverlay text="{}" font-desc="Sans, 12"'.format(text_overlay)

            launch_cmd += ' ! timeoverlay font-desc="Sans, {}"'.format(12 if time_overlay else 1e-3)
            launch_cmd += " ! queue"

            logger.debug("Creating pipeline from launch command %s ..", launch_cmd)
        else:
            error_image_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets", "error.jpg")
            launch_cmd += "filesrc location={}".format(error_image_location)
            launch_cmd += " ! jpegparse ! jpegdec ! imagefreeze"
            if text_overlay:
                launch_cmd += ' ! textoverlay text="{}\n{}"'.format("%s not found" % filename, text_overlay)
            launch_cmd += " ! videoconvert"

        launch_cmd += " ! ximagesink"  # or ! fakesink sync=true # sync required for realtime playback

        logger.debug("gst-launch-1.0 -v %s", launch_cmd)
        self._pipeline = Gst.parse_launch(launch_cmd)

        self._pipeline.get_bus().enable_sync_message_emission()
        self._pipeline.get_bus().add_signal_watch()

        self._pipeline.get_bus().connect('sync-message::element', self._on_bus_sync_msg)

    def _destroy_pipeline(self):
        if self._pipeline is not None:
            self._pipeline.set_state(Gst.State.NULL)
            self._pipeline = None

    def _on_bus_sync_msg(self, bus, msg):
        if msg is not None:
            sink = msg.src
            sink.set_property("force-aspect-ratio", True)
            sink.set_window_handle(self._movie_view.get_property('window').get_xid())

    def close(self):
        self.stop()
        Gtk.main_quit()
        logger.info("Waiting for the GTK Thread to join ..")
        self._gobject_thread.join()

    def play(self, filename, base_time_nsecs, videocrop_config, text_overlay, time_overlay):
        # Make sure the client clock is in sync with the server
        sync_grace = time.time() + 5.0
        delta = (base_time_nsecs - self._clock.get_time()) / 1e9
        while delta > ONE_MINUTE_SECONDS or delta < 0:
            delta = (base_time_nsecs - self._clock.get_time()) / 1e9
            time.sleep(0.1)
            if time.time() > sync_grace:
                msg = 'Delta between clock and base_time negative or too large: {} > ONE_MINUTE_SECONDS ({})' \
                    .format(delta, ONE_MINUTE_SECONDS)
                raise PlayerException(msg)

        if self._pipeline:
            self._destroy_pipeline()
        self._construct_pipeline(filename, videocrop_config, text_overlay, time_overlay)

        self._pipeline.set_start_time(Gst.CLOCK_TIME_NONE)
        self._pipeline.use_clock(self._clock)
        self._pipeline.set_base_time(base_time_nsecs)

        self._pipeline.set_state(Gst.State.PLAYING)

        # Make sure we have transitioned to the PLAYING state
        play_grace = time.time() + 5.0
        ret, state, pending = self._pipeline.get_state(timeout=Gst.SECOND)
        while state != Gst.State.PLAYING:
            ret, state, pending = self._pipeline.get_state(timeout=Gst.SECOND)
            time.sleep(0.1)
            if time.time() > play_grace:
                msg = 'Transition to playing state took too long!'
                raise PlayerException(msg)

        logger.info('play(base_time_nsecs=%d, clock_time_nsecs=%d)', base_time_nsecs, self._clock.get_time())

    def stop(self):
        self._destroy_pipeline()

    def is_playing(self):
        ret, state, pending = self._pipeline.get_state(timeout=Gst.SECOND)
        return state == Gst.State.PLAYING

    def get_duration(self):
        _, duration = self._pipeline.query_duration(Gst.Format.TIME)
        return round(duration / 1e9, 2)

    def get_position(self):
        _, position = self._pipeline.query_position(Gst.Format.TIME)
        return round(position / 1e9, 2)
