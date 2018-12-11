import logging
import socket
import time
from collections import namedtuple

import tornado

from .media_manager import MediaManagerServer
from .networking import NetworkingServer
from .networking.message_definition import ServerPlayBroadcastMessage, ServerBroadcastMessage
from .player import PlayerServer

logger = logging.getLogger(__name__)

RemoteClient = namedtuple('RemoteClient', 'username ip media_path age')


class Server(object):
    def __init__(self, media_path, base_time_offset, ip, server_broadcast_port, server_play_broadcast_port,
                 server_clock_port, server_broadcast_interval, client_broadcast_port):
        self._networking = NetworkingServer(server_broadcast_port, server_play_broadcast_port, client_broadcast_port)
        self._player = PlayerServer(ip, server_clock_port)
        self._base_time_offset = base_time_offset
        self._media_manager = MediaManagerServer(media_path)
        self._media_filename = None

        self._server_broadcast_timer = tornado.ioloop.PeriodicCallback(self._server_broadcast,
                                                                       server_broadcast_interval * 1e3)
        self._server_broadcast_timer.start()

        self._receive_client_broadcast_timer = tornado.ioloop.PeriodicCallback(self._receive_client_broadcast, 10)
        self._receive_client_broadcast_timer.start()

        self._check_done_timer = tornado.ioloop.PeriodicCallback(self._check_player_done, 100)
        self._check_done_timer.start()

        self._clients = {}
        self._client_config = {}

    def _server_broadcast(self):
        self._networking.send_broadcast(ServerBroadcastMessage(
            clock_ip=self._player.get_ip(),
            clock_port=self._player.get_port()
        ))

    def _receive_client_broadcast(self):
        try:
            msg = self._networking.receive_client_broadcast()
        except socket.timeout:
            pass
        except Exception as e:
            logger.error(e)
        else:
            self._clients[msg.ip] = {
                "time": time.time(),
                "msg": msg
            }

    def _check_player_done(self):
        if self._media_filename and not self._player.is_playing():
            self.play(self._media_filename)

    def get_media_filenames(self):
        return self._media_manager.get_filenames()

    def play(self, filename):
        self._media_filename = filename
        self._player.play(self._media_manager.get_full_path(filename), self._base_time_offset)
        self._networking.send_play_broadcast(ServerPlayBroadcastMessage(
            filename=filename,
            base_time_nsecs=self._player.get_base_time_nsecs(),
            time_overlay=True,
            client_config=self._client_config
        ))

    def set_client_config(self, config):
        self._client_config = config

    def get_client_config(self):
        return self._client_config

    def is_playing(self):
        return self._player.is_playing()

    def delete_media(self, filename):
        self._media_manager.delete_media(filename)

    def close(self):
        self._player.close()

    def get_duration(self):
        return self._player.get_duration()

    def get_position(self):
        return self._player.get_position()

    def get_clients(self):
        now = time.time()
        return [{
            "username": c["msg"].username,
            "ip": c["msg"].ip,
            "media_path": c["msg"].media_path,
            "age": now - c["time"]
        } for c in self._clients.values()]

    def sync_media(self):
        logger.info("Syncing media ..")
        self._media_manager.sync(
            ["{}@{}:{}".format(c["username"], c["ip"], c["media_path"]) for c in self.get_clients()])
        logger.info("Done syncing media")

    def get_media_path(self):
        return self._media_manager.get_media_path()

    def get_current_media_filename(self):
        return self._media_filename

    def get_state_dict(self):
        return {
            "player": {
                "media_path": self.get_media_path(),
                "media_filenames": self.get_media_filenames(),
                "current_media_filename": self.get_current_media_filename(),
                "is_playing": self.is_playing(),
                "duration": self.get_duration(),
                "position": self.get_position()
            },
            "client_config": self.get_client_config(),
            "clients": self.get_clients()
        }
