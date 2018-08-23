import logging
from videowall.gi_version import Gst, GstNet

from .player import Player
from .player_exceptions import PlayerException

logger = logging.getLogger(__name__)


class PlayerClient(Player):
    def __init__(self, player_platform, filename, base_time, ip, port):
        super(PlayerClient, self).__init__(player_platform, filename, ip, port, True)

        if not isinstance(base_time, int):
            raise PlayerException("Base time should be an integer, current value: {}".format(base_time))

        self._setup_net_client_clock(base_time)

        logger.debug("PlayerClient(player_platform=%s, filename=%s, base_time=%d, ip=%s, port=%s) constructed",
                     player_platform, filename, base_time, ip, port)

    def _setup_net_client_clock(self, base_time):
        self._pipeline.set_start_time(Gst.CLOCK_TIME_NONE)

        clock_name = "clock0"
        try:
            clock = GstNet.NetClientClock.new(clock_name, self._ip, self._port, base_time)
        except TypeError as e:
            raise PlayerException("GstNet.NetClientClock.new({}, {}, {}, {}) failed ({}). Set environment variable "
                                  "GST_DEBUG=1 for more info".format(clock_name, self._ip, self._port, base_time, e))

        self._pipeline.set_base_time(base_time)
        self._pipeline.use_clock(clock)
