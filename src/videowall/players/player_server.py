import logging
from videowall.gi_version import Gst, GstNet

from .player import Player

logger = logging.getLogger(__name__)


class PlayerServer(Player):
    def __init__(self, player_platform, filename, ip, port, gui):
        super(PlayerServer, self).__init__(player_platform, filename, ip, port, gui, 0, 0)
        self._setup_net_time_provider(port)

        logger.debug("PlayerServer(player_platform=%s, filename=%s, ip=%s, port=%s) constructed",
                     player_platform, filename, ip, port)

    def _setup_net_time_provider(self, port):
        self._clock = Gst.SystemClock.obtain()
        self._pipeline.use_clock(self._clock)
        self._clock_provider = GstNet.NetTimeProvider.new(self._clock, None, port)

    def play(self, seek_time=0):
        super(PlayerServer, self).play(
            base_time=self._clock.get_time(),
            seek_time=seek_time
        )
