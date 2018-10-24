import json
import logging
import socket
import threading
import time
from collections import namedtuple

from .message_definition import ServerPlayBroadcastMessage, ClientBroadcastMessage, ServerBroadcastMessage
from .networking_exceptions import NetworkingException

logger = logging.getLogger(__name__)

RemoteClient = namedtuple('RemoteClient', 'username ip media_path age')


class NetworkingServer(object):
    def __init__(self, server_broadcast_port, server_play_broadcast_port, client_broadcast_port, buffer_size=1024):
        self._server_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._server_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._server_broadcast_port = server_broadcast_port
        self._server_play_broadcast_port = server_play_broadcast_port

        self._client_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self._client_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._client_broadcast_socket.bind(("", client_broadcast_port))  # Bind to all
        self._client_broadcast_socket.settimeout(5.0)

        self._server_play_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._server_play_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self._clients = {}
        self._close = False

        def receive_client_broadcast():
            while not self._close:
                logger.debug("waiting for client broadcast message ...")

                try:
                    data, _ = self._client_broadcast_socket.recvfrom(buffer_size)
                except socket.timeout:
                    pass
                else:
                    try:
                        msg = ClientBroadcastMessage(**json.loads(data.decode("utf-8")))
                    except Exception as e:
                        logging.error("Received invalid ClientBroadcastMessage %s : error: %s", data, e)
                    else:
                        logger.debug("Client broadcast received: %s", msg)
                        self._clients[msg.ip] = {
                            "time": time.time(),
                            "msg": msg
                        }

        self._receive_client_broadcast_thread = threading.Thread(target=receive_client_broadcast)
        self._receive_client_broadcast_thread.start()

    def send_play_broadcast(self, msg):
        if not isinstance(msg, ServerPlayBroadcastMessage):
            raise NetworkingException("msg ({}) is not of type ServerPlayBroadcastMessage".format(msg))

        logger.debug("Sending %s", msg)
        self._server_broadcast_socket.sendto(json.dumps(msg.to_dict()).encode('utf-8'),
                                             ('<broadcast>', self._server_play_broadcast_port))

    def send_broadcast(self, msg):
        if not isinstance(msg, ServerBroadcastMessage):
            raise NetworkingException("msg ({}) is not of type ServerBroadcastMessage".format(msg))

        logger.debug("Sending %s", msg)
        self._server_broadcast_socket.sendto(json.dumps(msg.to_dict()).encode('utf-8'),
                                             ('<broadcast>', self._server_broadcast_port))

    def get_clients(self):
        now = time.time()
        return [RemoteClient(
            c["msg"].username,
            c["msg"].ip,
            c["msg"].media_path,
            now - c["time"]
        ) for c in self._clients.values()]

    def close(self):
        self._close = True
        self._receive_client_broadcast_thread.join()
