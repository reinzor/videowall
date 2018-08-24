import logging

from videowall.gi_version import GstNet
from videowall.util import validate_ip_port

from .player import Player
from .player_exceptions import PlayerException

logger = logging.getLogger(__name__)


class PlayerClient(Player):
    def __init__(self, player_platform, filename, ip, clock_port, videocrop_config):
        super(PlayerClient, self).__init__(player_platform, filename, True, videocrop_config)

        self._setup_net_client_clock(ip, clock_port)

        logger.debug("PlayerClient(player_platform=%s, filename=%s, ip=%s, port=%s) constructed",
                     player_platform, filename, ip, clock_port)

    def _setup_net_client_clock(self, ip, port):
        validate_ip_port(ip, port)

        clock_name = "clock0"
        try:
            clock = GstNet.NetClientClock.new(clock_name, ip, port, 0)
        except TypeError as e:
            raise PlayerException("GstNet.NetClientClock.new({}, {}, {}) failed ({}). Set environment variable "
                                  "GST_DEBUG=1 for more info".format(clock_name, ip, port, e))
        self._pipeline.use_clock(clock)
