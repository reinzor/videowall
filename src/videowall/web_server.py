import logging
import os.path
import re
import uuid

import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from videowall.server import Server
from videowall.util import get_unique_filename

logger = logging.getLogger(__name__)


class WebServer(tornado.web.Application):
    def __init__(self, server_web_port, media_path, base_time_offset, ip, server_broadcast_port,
                 server_play_broadcast_port, server_clock_port,
                 server_broadcast_interval, client_broadcast_port):
        self._server = Server(media_path, base_time_offset, ip, server_broadcast_port, server_play_broadcast_port,
                              server_clock_port, server_broadcast_interval, client_broadcast_port)

        self._server_web_port = server_web_port

        UploadHandler.path = self._server.get_media_path()
        WebSocketHandler.server = self._server
        super(WebServer, self).__init__([
            ("/upload", UploadHandler),
            ("/ws", WebSocketHandler),
            ("/(.*)", tornado.web.StaticFileHandler, {
                "path": os.path.join(os.path.dirname(__file__), "../../web/dist/"),
                "default_filename": "index.html"
            }),
        ])
        self.listen(self._server_web_port)

    def run(self):
        tornado.ioloop.IOLoop.current().start()


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def initialize(self):
        WebSocketHandler.server.play("/home/rein/Videos/big_buck_bunny_720p_30mb.mp4", True, {})

    def data_received(self, chunk):
        pass

    def on_message(self, message):
        pass


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        file_info = self.request.files['file'][0]
        logger.info("Received upload: (content_type=%s, filename=%s)", file_info['content_type'], file_info['filename'])
        filename = get_unique_filename(os.path.join(UploadHandler.path, file_info['filename']))
        logger.info("Writing to %s", filename)
        file_handle = open(filename, 'w')
        file_handle.write(file_info['body'])
        logger.info("Wrote to %s", filename)
        self.finish("Uploaded {}".format(filename))
