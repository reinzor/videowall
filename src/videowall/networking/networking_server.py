import json
import logging
import socket

from .message_definition import ServerPlayBroadcastMessage, ClientBroadcastMessage, ServerBroadcastMessage
from .networking_exceptions import NetworkingException

logger = logging.getLogger(__name__)


class NetworkingServer(object):
    def __init__(self, server_broadcast_port, server_play_broadcast_port, client_broadcast_port, buffer_size=1024):
        self._server_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._server_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._server_broadcast_port = server_broadcast_port
        self._server_play_broadcast_port = server_play_broadcast_port

        self._client_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self._client_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._client_broadcast_socket.bind(("", client_broadcast_port))  # Bind to all
        self._client_broadcast_socket.settimeout(1e-4)

        self._server_play_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._server_play_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self._buffer_size = buffer_size

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

    def receive_client_broadcast(self):
        data, _ = self._client_broadcast_socket.recvfrom(self._buffer_size)

        try:
            msg = ClientBroadcastMessage(**json.loads(data.decode("utf-8")))
        except Exception as e:
            raise NetworkingException(e)
        else:
            logger.debug("Client broadcast received: %s", msg)
            return msg
