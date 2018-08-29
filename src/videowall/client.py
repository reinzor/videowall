import logging

from videowall.networking import NetworkingClient
from videowall.networking.message_definition import ClientConfig
from videowall.players import PlayerClient

logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, ip, player_platform, broadcast_port):
        self._networking = NetworkingClient(ip, broadcast_port)
        self._player = PlayerClient(player_platform, True, ip)

    @staticmethod
    def _get_client_specific_config(ip, client_config):
        if ip in client_config:
            return client_config[ip]
        logging.warn("%s not present in client_config %s, using default config", ip, client_config)
        return ClientConfig.get_default()

    def run(self):
        while True:
            msg = self._networking.receive_broadcast()
            client_cfg = Client._get_client_specific_config(self._networking.get_ip(), msg.client_config)

            self._player.play(msg.filename, msg.base_time, msg.ip, msg.clock_port, client_cfg.videocrop_config)

    def close(self):
        self._player.close()
