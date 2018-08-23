import logging
from videowall.gi_version import Gst, GstNet

from .player import Player

logger = logging.getLogger(__name__)


class PlayerServer(Player):
    def __init__(self, player_platform, filename, ip, port, gui):
        super(PlayerServer, self).__init__(player_platform, filename, ip, port, gui)
        self._setup_net_time_provider(port)

        logger.debug("PlayerServer(player_platform=%s, filename=%s, base_time=%s, ip=%s, port=%s) constructed",
                     player_platform, filename, self._base_time, ip, port)

    def _setup_net_time_provider(self, port):
        clock = Gst.SystemClock.obtain()
        self._pipeline.use_clock(clock)
        self._clock_provider = GstNet.NetTimeProvider.new(clock, None, port)

        self._base_time = clock.get_time()

        self._pipeline.set_start_time(Gst.CLOCK_TIME_NONE)
        self._pipeline.set_base_time(self._base_time)
