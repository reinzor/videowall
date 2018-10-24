import logging
import threading
import time

from .networking import NetworkingServer
from .networking.message_definition import ServerPlayBroadcastMessage, ServerBroadcastMessage
from .media_manager import MediaManagerServer
from .player import PlayerServer

logger = logging.getLogger(__name__)


class Server(object):
    def __init__(self, media_path, base_time_offset, ip, server_broadcast_port, server_play_broadcast_port,
                 server_clock_port, server_broadcast_interval, client_broadcast_port, client_config_dict):
        self._networking = NetworkingServer(server_broadcast_port, server_play_broadcast_port, client_broadcast_port)
        self._player = PlayerServer(ip, server_clock_port)
        self._base_time_offset = base_time_offset
        self._client_config_dict = client_config_dict
        self._media_manager = MediaManagerServer(media_path)

        self._close = False

        self._server_broadcast_interval = server_broadcast_interval
        self._server_broadcast_thread = threading.Thread(target=self.send_server_broadcast)
        self._server_broadcast_thread.start()

    def send_server_broadcast(self):
        while not self._close:
            self._networking.send_broadcast(ServerBroadcastMessage(
                clock_ip=self._player.get_ip(),
                clock_port=self._player.get_port()
            ))
            time.sleep(self._server_broadcast_interval)

    def get_media_filenames(self):
        return self._media_manager.get_filenames()

    def play(self, filename, time_overlay):
        self._player.play(self._media_manager.get_full_path(filename), self._base_time_offset)
        self._networking.send_play_broadcast(ServerPlayBroadcastMessage(
            filename=filename,
            base_time_nsecs=self._player.get_base_time_nsecs(),
            time_overlay=time_overlay,
            client_config={ip: cfg for ip, cfg in self._client_config_dict.items()}
        ))

    def is_playing(self):
        return self._player.is_playing()

    def close(self):
        self._close = True
        self._networking.close()
        self._player.close()

    def get_duration(self):
        return self._player.get_duration()

    def get_position(self):
        return self._player.get_position()

    def get_clients(self):
        return self._networking.get_clients()

    def sync_media(self, remote_paths):
        self._media_manager.sync(remote_paths)
