import json
import logging
import socket

from message_definition import BroadcastMessage
from networking_exceptions import NetworkingException

logger = logging.getLogger(__name__)


class NetworkingClient(object):
    def __init__(self, broadcast_port, buffer_size=1024):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._socket.bind(("", broadcast_port))  # Bind to all
        self._buffer_size = buffer_size

    def receive_broadcast(self):
        data, _ = self._socket.recvfrom(self._buffer_size)

        try:
            msg = BroadcastMessage(**json.loads(data))
        except Exception as e:
            raise NetworkingException(e)
        else:
            logger.debug("Received %s", msg)
            return msg
