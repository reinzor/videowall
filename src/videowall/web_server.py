import logging

from flask import Flask
from flask_socketio import SocketIO
from videowall.server import Server

logger = logging.getLogger(__name__)


class WebServer:
    def __init__(self, webserver_port, media_path, base_time_offset, ip, server_broadcast_port,
                 server_play_broadcast_port,
                 server_clock_port, server_broadcast_interval, client_broadcast_port):
        self._server = Server(media_path, base_time_offset, ip, server_broadcast_port, server_play_broadcast_port,
                              server_clock_port, server_broadcast_interval, client_broadcast_port, {})
        self._ip = ip
        self._port = webserver_port
        self._app = Flask(__name__)
        self._app.config['SECRET_KEY'] = 'secret!'
        self._socketio = SocketIO(self._app)

    def run(self):
        @self._socketio.on('connect')
        def on_connect():
            logger.info("Client connected")

        @self._socketio.on('disconnect')
        def on_disconnect():
            logger.info("Client disconnect")

        @self._socketio.on('test')
        def on_test(msg):
            logger.info("Test message: %s", msg)

        try:
            self._socketio.run(self._app, host=self._ip, port=self._port)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt")
