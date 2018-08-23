import logging
import time

from .networking import NetworkingServer
from .networking.message_definition import BroadcastMessage, ClientConfig
from .players import PlayerServer

logger = logging.getLogger(__name__)


class Server(object):
    def __init__(self, broadcast_port, broadcast_interval, player_platform, filename, player_ip, player_port, gui,
                 client_seek_lookahead, client_seek_grace_time, client_config_dict):
        self._networking = NetworkingServer(broadcast_port)
        self._player = PlayerServer(player_platform, filename, player_ip, player_port, gui)

        self._broadcast_interval = broadcast_interval
        self._client_seek_lookahead = client_seek_lookahead
        self._client_seek_grace_time = client_seek_grace_time
        self._client_config_dict = client_config_dict

    def run(self):
        while True:
            self._player.play()
            logger.info("Started player, broadcasting with interval %.2f [seconds] ..", self._broadcast_interval)

            while self._player.is_playing():
                self._networking.send_broadcast(BroadcastMessage(
                    filename=self._player.get_filename(),
                    base_time=self._player.get_base_time(),
                    position=self._player.get_position(),
                    seek_grace_time=self._client_seek_grace_time,
                    seek_lookahead=self._client_seek_lookahead,
                    duration=self._player.get_duration(),
                    player_ip=self._player.get_ip(),
                    player_port=self._player.get_port(),
                    client_config={ip: cfg for ip, cfg in self._client_config_dict.iteritems()}
                ))
                time.sleep(self._broadcast_interval)

            logger.info("Player not playing anymore, looping ...")
