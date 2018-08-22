import logging
import os.path
import socket
from gi.repository import Gst

from player_exceptions import PlayerException
from player_platforms import PlayerPlatform

logger = logging.getLogger(__name__)


class Player(object):
    Gst.init(None)

    def __init__(self, player_platform, filename, ip, port, gui):
        if not isinstance(player_platform, PlayerPlatform):
            raise PlayerException("Invalid player platform {}, available platforms: {}".format(player_platform,
                                                                                               list(PlayerPlatform)))

        real_path = os.path.realpath(os.path.expanduser(filename))
        if not os.path.isfile(real_path):
            raise PlayerException("File '{}' does not exist!".format(filename))

        try:
            socket.inet_pton(socket.AF_INET, ip)
        except socket.error as e:
            raise PlayerException(e)

        if not isinstance(port, int):
            raise PlayerException("Port should be an integer")

        if not isinstance(gui, bool):
            raise PlayerException("GUI should be a boolean")

        self._player_platform = player_platform
        self._filename = filename
        self._ip = ip
        self._port = port
        self._pipeline = self._get_pipeline(filename, player_platform, gui)

        logger.debug("Player constructed")

    @staticmethod
    def _get_pipeline(filename, player_platform, gui):
        launch_cmd = "filesrc location={}".format(filename)

        if player_platform == PlayerPlatform.X86_64:
            launch_cmd += " ! decodebin"
        elif player_platform == PlayerPlatform.RASPBERRY_PI:
            launch_cmd += " ! qtdemux ! h264parse ! omxh264dec"

        if gui:
            launch_cmd += " ! videoconvert ! queue ! ximagesink"
        else:
            launch_cmd += " ! fakesink"

        logger.debug("Creating pipeline from launch command %s ..", launch_cmd)

        pipeline = Gst.parse_launch(launch_cmd)
        pipeline.set_state(Gst.State.PAUSED)
        return pipeline

    def play(self):
        self._pipeline.set_state(Gst.State.PLAYING)
        self._pipeline.get_bus().poll(Gst.MessageType.EOS | Gst.MessageType.ERROR, Gst.CLOCK_TIME_NONE)
        self._pipeline.set_state(Gst.State.NULL)
