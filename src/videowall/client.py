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
            if self._player is None or self._player.get_filename() != msg.filename:
                self._player = PlayerClient(self._player_platform, msg.filename, msg.base_time, msg.player_ip,
                                            msg.player_port)
                self._player.play()
