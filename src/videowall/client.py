import logging

from videowall.networking import NetworkingClient
from videowall.networking.message_definition import ClientConfig
from videowall.players import PlayerClient

logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, ip, player_platform, broadcast_port):
        self._networking = NetworkingClient(ip, broadcast_port)
        self._player = PlayerClient(player_platform)

    def _get_client_specific_config(self, client_config):
        if self._networking.get_ip() in client_config:
            return client_config[self._networking.get_ip()]
        logging.warn("%s not present in client_config %s, using default config", self._networking.get_ip(),
                     client_config)
        return ClientConfig.get_default()

    def run(self):
        while True:
            msg = self._networking.receive_broadcast()
            client_cfg = self._get_client_specific_config(msg.client_config)

            self._player.play(msg.filename, msg.base_time, msg.ip, msg.clock_port, client_cfg.videocrop_config)

    def close(self):
        self._player.close()
