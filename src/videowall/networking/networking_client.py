import json
import logging
import socket
import threading
import time

from videowall.util import validate_ip_port, validate_positive_int_argument

from .message_definition import ServerBroadcastMessage, ClientBroadcastMessage
from .networking_exceptions import NetworkingException

logger = logging.getLogger(__name__)


class NetworkingClient(object):
    def __init__(self, ip, server_broadcast_port, client_broadcast_port, client_broadcast_interval, buffer_size=1024):
        validate_ip_port(ip, server_broadcast_port)
        validate_positive_int_argument(client_broadcast_port)
        self._ip = ip

        self._server_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self._server_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._server_broadcast_socket.bind(("", server_broadcast_port))  # Bind to all
        self._server_broadcast_socket.settimeout(5.0)
        self._buffer_size = buffer_size

        self._client_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._client_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._client_broadcast_port = client_broadcast_port

        self._close = False

        def send_client_broadcast():
            while not self._close:
                msg = ClientBroadcastMessage(ip)
                logger.debug("Broadcasting client message: %s", msg)
                self._client_broadcast_socket.sendto(json.dumps(msg.to_dict()), ('<broadcast>', client_broadcast_port))
                time.sleep(client_broadcast_interval)

        self._client_broadcast_thread = threading.Thread(target=send_client_broadcast)
        self._client_broadcast_thread.start()

    def receive_server_broadcast(self):
        logger.debug("waiting for server broadcast message ...")

        # May raise a socket.timeout exception
        data, _ = self._server_broadcast_socket.recvfrom(self._buffer_size)

        try:
            msg = ServerBroadcastMessage(**json.loads(data))
        except Exception as e:
            raise NetworkingException(e)
        else:
            logger.debug("Server broadcast received: %s", msg)
            return msg

    def get_ip(self):
        return self._ip

    def close(self):
        logger.debug("Closing NetworkingClient ...")
        self._close = True
        self._client_broadcast_thread.join()
