import logging

from videowall.gi_version import GstNet, GLib, Gst
from videowall.networking.message_definition import VideocropConfig
from videowall.util import validate_ip_port

from .player import Player
from .player_exceptions import PlayerException

logger = logging.getLogger(__name__)


class PlayerClient(Player):
    def __init__(self, player_platform):
        super(PlayerClient, self).__init__(player_platform, True, "PlayerClient")

        logger.debug("PlayerClient(player_platform=%s) constructed", player_platform)

    def _g_construct_pipeline_with_clock_client(self, filename, base_time, ip, port, videocrop_config):
        self._g_construct_pipeline(filename, videocrop_config)
        self._g_pipeline.set_start_time(Gst.CLOCK_TIME_NONE)

        clock_name = "clock0"
        try:
            clock = GstNet.NetClientClock.new(clock_name, ip, port, 0)
        except TypeError as e:
            raise PlayerException("GstNet.NetClientClock.new({}, {}, {}) failed ({}). Set environment variable "
                                  "GST_DEBUG=1 for more info".format(clock_name, ip, port, e))

        self._g_pipeline.set_base_time(base_time)
        self._g_pipeline.use_clock(clock)

    def play(self, filename, base_time, ip, port, videocrop_config=VideocropConfig(0, 0, 0, 0)):
        validate_ip_port(ip, port)

        self.stop()

        GLib.idle_add(self._g_construct_pipeline_with_clock_client, filename, base_time, ip, port, videocrop_config)
        self._wait_for_state(Gst.State.PLAYING)
