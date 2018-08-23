import logging

from videowall.networking import NetworkingClient
from videowall.players import PlayerClient

logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, broadcast_port, player_platform):
        self._networking = NetworkingClient(broadcast_port)
        self._player = None

        self._player_platform = player_platform

    def run(self):
        while True:
            msg = self._networking.receive_broadcast()

            # This can be done in the constructor in the future if we can set filesrcs dynamically
            if self._player is None:
                self._player = PlayerClient(self._player_platform, msg.filename, msg.player_ip, msg.player_port)

            if self._player.get_base_time() != msg.base_time:
                self._player.play(
                    base_time=msg.base_time,
                    seek_time=msg.seek_time
                )
