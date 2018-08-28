import logging

from .networking import NetworkingServer
from .networking.message_definition import BroadcastMessage, ClientConfig
from .players import PlayerServer

logger = logging.getLogger(__name__)


class Server(object):
    def __init__(self, player_platform, ip, broadcast_port, clock_port, gui, client_config_dict):
        self._networking = NetworkingServer(broadcast_port)
        self._player = PlayerServer(player_platform, ip, clock_port, gui)

        self._client_config_dict = client_config_dict

    def play(self, filename):
        self._player.play(filename)
        self._networking.send_broadcast(BroadcastMessage(
            filename=self._player.get_filename(),
            base_time=self._player.get_base_time(),
            ip=self._player.get_ip(),
            clock_port=self._player.get_port(),
            client_config={ip: cfg for ip, cfg in self._client_config_dict.iteritems()}
        ))

    def is_playing(self):
        return self._player.is_playing()