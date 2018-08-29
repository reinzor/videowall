import logging

from .networking import NetworkingServer
from .networking.message_definition import BroadcastMessage
from .players import PlayerServer

logger = logging.getLogger(__name__)


class Server(object):
    def __init__(self, player_platform, base_time_offset, ip, broadcast_port, clock_port, client_config_dict):
        self._networking = NetworkingServer(broadcast_port)
        self._player = PlayerServer(player_platform, ip, clock_port)
        self._base_time_offset = base_time_offset

        self._client_config_dict = client_config_dict

    def play(self, filename):
        self._player.play(filename, self._base_time_offset)
        self._networking.send_broadcast(BroadcastMessage(
            filename=self._player.get_filename(),
            base_time=self._player.get_base_time(),
            ip=self._player.get_ip(),
            clock_port=self._player.get_port(),
            client_config={ip: cfg for ip, cfg in self._client_config_dict.iteritems()}
        ))

    def is_playing(self):
        return self._player.is_playing()

    def close(self):
        self._player.close()

    def get_duration_seconds(self):
        return self._player.get_duration_seconds()

    def get_position_seconds(self):
        return self._player.get_position_seconds()
