import json
import socket
import logging

from .message_definition import BroadcastMessage
from .networking_exceptions import NetworkingException

logger = logging.getLogger(__name__)


class NetworkingServer(object):
    def __init__(self, broadcast_port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._broadcast_port = broadcast_port

    def send_broadcast(self, msg):
        if not isinstance(msg, BroadcastMessage):
            raise NetworkingException("msg ({}) is not of type NetworkingException".format(msg))

        logger.debug("Sending %s", msg)
        self._socket.sendto(json.dumps(msg.to_dict()), ('<broadcast>', self._broadcast_port))
