import logging
import os.path
import uuid

import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from videowall.server import Server

logger = logging.getLogger(__name__)


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
