import logging
import time
from pymediainfo import MediaInfo

from videowall.gi_version import Gst, GstNet, GLib
from videowall.networking.message_definition import VideocropConfig
from videowall.util import validate_ip_port

from .player import Player
from .player_exceptions import PlayerException

logger = logging.getLogger(__name__)


class PlayerServer(object):
    def __init__(self, player_platform, ip, port):
        validate_ip_port(ip, port)

        self._ip = ip
        self._port = port
        self._base_time = None
        self._duration = 0

        logger.debug("PlayerServer(player_platform=%s, ip=%s, port=%s) constructed", player_platform, ip, port)

    def play(self, filename, base_time_offset, videocrop_config=VideocropConfig(0, 0, 0, 0)):
        info = MediaInfo.parse(filename)

        for track in info.tracks:
            if track.track_type == 'Video':
                video_track = track
                break
        else:
            raise Exception()

        self._start = time.time() + base_time_offset / 1e9
        self._duration = video_track.duration / 1e3

        clock = Gst.SystemClock.obtain()
        # self._g_pipeline.use_clock(clock)
        self._g_clock_provider = GstNet.NetTimeProvider.new(clock, None, self._port)

        self._base_time = clock.get_time() + base_time_offset
        # self._wait_for_state(Gst.State.PLAYING)

    def get_ip(self):
        return self._ip

    def get_port(self):
        return self._port

    def get_base_time(self):
        if self._base_time is None:
            raise PlayerException('No base time available, please first play a file')
        return self._base_time

    def get_position_seconds(self):
        return max(0, time.time() - self._start)

    def get_duration_seconds(self):
        return self._duration

    def stop(self):
        pass

    def is_playing(self):
        return True
