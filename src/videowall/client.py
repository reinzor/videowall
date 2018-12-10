import getpass
import logging
import socket
import threading
import time

from videowall.player.player_exceptions import PlayerException

from .media_manager import MediaManagerClient
from .networking import NetworkingClient
from .networking.message_definition import ClientConfig, ClientBroadcastMessage
from .player import PlayerClient

logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, player_platform, media_path, ip, server_broadcast_port, server_play_broadcast_port,
                 client_broadcast_port, client_broadcast_interval):
        self._networking = NetworkingClient(ip, server_broadcast_port, server_play_broadcast_port,
                                            client_broadcast_port)
        self._player_platform = player_platform
        self._player = None
        self._media_manager = MediaManagerClient(media_path)

        self._close = False

        self._client_broadcast_interval = client_broadcast_interval
        self._client_broadcast_thread = threading.Thread(target=self.send_client_broadcast)
        self._client_broadcast_thread.start()

    def send_client_broadcast(self):
        while not self._close:
            msg = ClientBroadcastMessage(
                getpass.getuser(),
                self._networking.get_ip(),
                self._media_manager.get_media_path()
            )
            logger.debug("Broadcasting client message: %s", msg)
            self._networking.send_client_broadcast(msg)
            time.sleep(self._client_broadcast_interval)

    @staticmethod
    def _get_client_specific_config(ip, client_config):
        if ip in client_config:
            return client_config[ip]
        logging.warn("%s not present in client_config %s, using default config", ip, client_config)
        return ClientConfig.get_default()

    def run(self):
        while not self._close:
            try:
                logger.info("Waiting for server broadcast message ...")
                msg = self._networking.receive_server_broadcast()
            except socket.timeout:
                pass
            else:
                self._player = PlayerClient(self._player_platform, msg.clock_ip, msg.clock_port)
                break

        while not self._close:
            try:
                msg = self._networking.receive_server_play_broadcast()
            except socket.timeout:
                pass
            else:
                client_cfg = Client._get_client_specific_config(self._networking.get_ip(), msg.client_config)
                try:
                    self._player.play(self._media_manager.get_full_path(msg.filename), msg.base_time_nsecs,
                                      client_cfg.videocrop_config, self._networking.get_ip(), msg.time_overlay)
                except PlayerException as e:
                    logger.error(e)

    def close(self):
        self._networking.close()
        self._player.close()

        logger.debug("Closing Client ...")
        self._close = True
        self._client_broadcast_thread.join()
