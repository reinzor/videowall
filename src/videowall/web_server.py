import logging

#
# from flask import Flask
# from flask_socketio import SocketIO
#
from videowall.server import Server

logger = logging.getLogger(__name__)
#
#
# class WebServer:
#     def __init__(self, webserver_port, media_path, base_time_offset, ip, server_broadcast_port,
#                  server_play_broadcast_port,
#                  server_clock_port, server_broadcast_interval, client_broadcast_port):
#         self._server = Server(media_path, base_time_offset, ip, server_broadcast_port, server_play_broadcast_port,
#                               server_clock_port, server_broadcast_interval, client_broadcast_port, {})
#         self._ip = ip
#         self._port = webserver_port
#         self._app = Flask(__name__)
#         self._app.config['SECRET_KEY'] = 'secret!'
#         self._socketio = SocketIO(self._app)
#
#     def run(self):
#         @self._socketio.on('connect')
#         def on_connect():
#             logger.info("Client connected")
#
#         @self._socketio.on('disconnect')
#         def on_disconnect():
#             logger.info("Client disconnect")
#
#         @self._socketio.on('test')
#         def on_test(msg):
#             logger.info("Test message: %s", msg)
#
#         try:
#             self._socketio.run(self._app, host=self._ip, port=self._port)
#         except KeyboardInterrupt:
#             logger.info("KeyboardInterrupt")


# !/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Simplified chat demo for websockets.

Authentication, error handling, etc are left as an exercise for the reader :)
"""

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid


class WebServer(tornado.web.Application):
    def __init__(self, server_web_port, media_path, base_time_offset, ip, server_broadcast_port,
                 server_play_broadcast_port, server_clock_port,
                 server_broadcast_interval, client_broadcast_port):
        self._server = Server(media_path, base_time_offset, ip, server_broadcast_port, server_play_broadcast_port,
                              server_clock_port, server_broadcast_interval, client_broadcast_port)

        self._server_web_port = server_web_port

        super(WebServer, self).__init__([
            ("/api", WebSocketHandler, {"server": self._server}),
            ("/(.*)", tornado.web.StaticFileHandler, {
                "path": os.path.join(os.path.dirname(__file__), "../../web/dist/"),
                "default_filename": "index.html"
            }),
        ])
        self.listen(self._server_web_port)

    def run(self):
        tornado.ioloop.IOLoop.current().start()


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200
    server = None

    def initialize(self, server):
        WebSocketHandler.server = server
        server.play("/home/rein/Videos/big_buck_bunny_720p_30mb.mp4", True, {})
        print("init")

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        WebSocketHandler.waiters.add(self)

    def on_close(self):
        WebSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        chat = {"id": str(uuid.uuid4()), "body": parsed["body"]}
        chat["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=chat)
        )

        WebSocketHandler.update_cache(chat)
        WebSocketHandler.send_updates(chat)
