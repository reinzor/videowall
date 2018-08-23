import logging

from videowall.networking import NetworkingClient
from videowall.networking.message_definition import ClientConfig
from videowall.players import PlayerClient

logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, broadcast_port, player_platform, ip):
        self._networking = NetworkingClient(broadcast_port)
        self._player = None

        self._player_platform = player_platform
        self._ip = ip

    def _get_client_specific_config(self, client_config):
        if self._ip in client_config:
            return client_config[self._ip]
        logging.warn("%s not present in client_config %s, using default config", self._ip, client_config)
        return ClientConfig.get_default()

    def run(self):
        while True:
            msg = self._networking.receive_broadcast()
            client_cfg = self._get_client_specific_config(msg.client_config)

            # This can be done in the constructor in the future if we can set filesrcs dynamically
            if self._player is None:
                self._player = PlayerClient(self._player_platform, msg.filename, msg.player_ip, msg.player_port,
                                            msg.seek_grace_time, msg.seek_lookahead, client_cfg.videocrop_config)

            if self._player.get_base_time() != msg.base_time:
                logger.info("Received an updated base time, sending new play command to player ...")
                self._player.play(
                    base_time=msg.base_time,
                    seek_time=msg.position
                )
