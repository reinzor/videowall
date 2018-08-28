import logging
from videowall.gi_version import Gst, GstNet, GLib
from videowall.networking.message_definition import VideocropConfig
from videowall.util import validate_ip_port

from .player_exceptions import PlayerException

from .player import Player

logger = logging.getLogger(__name__)


class PlayerServer(Player):
    def __init__(self, player_platform, ip, port, show_gui):
        super(PlayerServer, self).__init__(player_platform, show_gui, "PlayerServer")
        validate_ip_port(ip, port)

        self._ip = ip
        self._port = port
        self._base_time = None

        logger.debug("PlayerServer(player_platform=%s, ip=%s, port=%s) constructed", player_platform, ip, port)

    def _g_construct_pipeline_with_clock_server(self, filename, videocrop_config):
        self._g_construct_pipeline(filename, videocrop_config)

        clock = Gst.SystemClock.obtain()
        self._g_pipeline.use_clock(clock)
        self._g_clock_provider = GstNet.NetTimeProvider.new(clock, None, self._port)

        self._base_time = clock.get_time()

        self._g_pipeline.set_start_time(Gst.CLOCK_TIME_NONE)
        self._g_pipeline.set_base_time(self._base_time)

    def play(self, filename, videocrop_config=VideocropConfig(0, 0, 0, 0)):
        self.stop()

        GLib.idle_add(self._g_construct_pipeline_with_clock_server, filename, videocrop_config)
        self._wait_for_state(Gst.State.PLAYING)

    def get_ip(self):
        return self._ip

    def get_port(self):
        return self._port

    def get_base_time(self):
        if self._base_time is None:
            raise PlayerException('No base time available, please first play a file')
        return self._base_time
