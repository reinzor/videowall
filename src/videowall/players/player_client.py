import logging

from videowall.gi_version import GstNet

from .player import Player
from .player_exceptions import PlayerException

logger = logging.getLogger(__name__)


class PlayerClient(Player):
    def __init__(self, player_platform, filename, ip, clock_port, seek_grace_time, seek_lookahead, videocrop_config):
        super(PlayerClient, self).__init__(player_platform, filename, ip, clock_port, True, seek_grace_time,
                                           seek_lookahead, videocrop_config)

        self._setup_net_client_clock()

        logger.debug("PlayerClient(player_platform=%s, filename=%s, ip=%s, port=%s) constructed",
                     player_platform, filename, ip, clock_port)

    def _setup_net_client_clock(self):
        clock_name = "clock0"
        try:
            clock = GstNet.NetClientClock.new(clock_name, self._ip, self._port, 0)
        except TypeError as e:
            raise PlayerException("GstNet.NetClientClock.new({}, {}, {}, {}) failed ({}). Set environment variable "
                                  "GST_DEBUG=1 for more info".format(clock_name, self._ip, self._port, base_time, e))
        self._pipeline.use_clock(clock)
