import inspect
import json
import logging
import os.path
import shutil
from tempfile import NamedTemporaryFile

import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from pymediainfo import MediaInfo
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
    def __init__(self, application, request, **kwargs):
        super(WebSocketHandler, self).__init__(application, request, **kwargs)
        self._broadcast_timer = tornado.ioloop.PeriodicCallback(self._broadcast, 100)

        self._command_handlers = {
            "play": self._play,
            "delete": self._delete,
            "set_client_config": self._set_client_config,
            "sync_media": self._sync_media
        }

    def check_origin(self, origin):
        """
        Allow external connections, e.g. dev server
        """
        return True

    def open(self):
        logger.info("New websocket connection!")
        self._broadcast_timer.start()

    def _broadcast(self):
        self.write_message(WebSocketHandler.server.get_state_dict())

    def on_message(self, message):
        try:
            message = json.loads(message)
        except Exception as e:
            logger.error("Could not decode command: {}".format(e))

        if "command" not in message or "arguments" not in message:
            logger.error("Message should contain a command and arguments key!")
            return

        cmd = message["command"]
        args = message["arguments"]

        logger.info("Command %s with arguments %s", cmd, args)

        if cmd in self._command_handlers:
            f = self._command_handlers[cmd]
            try:
                f(**args)
            except TypeError:
                logger.error(
                    "Invalid args for cmd {}. Received {} expected {}".format(cmd, args.keys(), inspect.getargspec(f)))
        else:
            logger.warning("No registered handler for command {}".format(message["command"]))

    def _delete(self, filename):
        WebSocketHandler.server.delete_media(filename)

    def _play(self, filename):
        try:
            WebSocketHandler.server.play(filename)
        except Exception as e:
            logger.error(e)

    def _set_client_config(self, config):
        WebSocketHandler.server.set_client_config(config)

    def _sync_media(self):
        WebSocketHandler.server.sync_media()

    def on_close(self):
        self._broadcast_timer.stop()


class UploadHandler(tornado.web.RequestHandler):
    @staticmethod
    def _validate_720p_mp4_file(filename):
        info = MediaInfo.parse(filename)

        for track in info.tracks:
            if track.track_type == 'Video':
                video_track = track
                if video_track.codec != 'AVC':
                    raise Exception("Video should have an AVC (h264) encoding")
                if video_track.width != 1280 or video_track.height != 720:
                    raise Exception(
                        "Video should be of size 1280x720, it is {}x{}".format(video_track.width, video_track.height))
                break
        else:
            raise Exception("File does not contain a video track")

    def post(self):
        file_info = self.request.files['file'][0]
        logger.info("Received upload: (content_type=%s, filename=%s)", file_info['content_type'], file_info['filename'])
        filename = get_unique_filename(os.path.join(UploadHandler.path, file_info['filename']))
        file_handle = NamedTemporaryFile(delete=False)
        file_handle.write(file_info['body'])
        file_handle.close()
        try:
            self._validate_720p_mp4_file(file_handle.name)
        except Exception as e:
            logger.error(e)
            self.set_status(400)
            self.finish({"reason": str(e)})
        else:
            logger.info("Writing to %s", filename)
            shutil.copyfile(file_handle.name, filename)
            logger.info("Wrote to %s", filename)
            self.finish("Uploaded {}".format(filename))
