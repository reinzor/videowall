import logging
import threading
import time

from .networking import NetworkingServer
from .networking.message_definition import BroadcastMessage
from .players import PlayerServer

logger = logging.getLogger(__name__)


class Server(object):
    def __init__(self, broadcast_port, broadcast_interval, player_platform, filename, player_ip, player_port, gui):
        self._networking = NetworkingServer(broadcast_port)
        self._player = PlayerServer(player_platform, filename, player_ip, player_port, gui)

        self._broadcast_interval = broadcast_interval

    def run(self):
        logger.debug("Starting player thread ..")
        player_thread = threading.Thread(target=self._player.play)
        player_thread.start()
        logger.debug("Started player thread, broadcasting with interval %.2f [seconds] ..", self._broadcast_interval)

        while self._player.is_playing():
            self._networking.send_broadcast(BroadcastMessage(
                filename=self._player.get_filename(),
                base_time=self._player.get_base_time(),
                player_ip=self._player.get_ip(),
                player_port=self._player.get_port()
            ))
            time.sleep(self._broadcast_interval)

        logger.debug("Player not playing anymore, waiting for thread join ...")
        player_thread.join()
