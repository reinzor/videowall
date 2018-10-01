import logging
import time

from pymediainfo import MediaInfo
from videowall.gi_version import Gst, GstNet
from videowall.util import validate_ip_port

from .player_exceptions import PlayerException

logger = logging.getLogger(__name__)


class PlayerServer(object):
    def __init__(self, ip, port):
        validate_ip_port(ip, port)

        self._ip = ip
        self._port = port
        self._base_time_nsecs = None
        self._duration = None
        self._start = None

        self._clock = Gst.SystemClock.obtain()
        self._clock_provider = GstNet.NetTimeProvider.new(self._clock, None, self._port)

        logger.debug("__init__(ip=%s, port=%s) constructed", ip, port)

    @staticmethod
    def _get_video_duration_from_file(filename):
        info = MediaInfo.parse(filename)

        for track in info.tracks:
            if track.track_type == 'Video':
                video_track = track
                break
        else:
            raise Exception()
        return round(video_track.duration / 1e3, 2)

    def play(self, filename, base_time_offset):
        self._start = time.time() + base_time_offset
        self._duration = self._get_video_duration_from_file(filename)
        self._base_time_nsecs = self._clock.get_time() + base_time_offset * 1e9

        logger.debug("play(start=%.2f, duration=%.2f, base_time_nsecs=%d, clock_time_nsecs=%d)", self._start,
                     self._duration, self._base_time_nsecs, self._clock.get_time())

    def get_ip(self):
        return self._ip

    def get_port(self):
        return self._port

    def get_base_time_nsecs(self):
        if self._base_time_nsecs is None:
            raise PlayerException('No base time available, please first play a file')
        return self._base_time_nsecs

    def get_position(self):
        return round(min(max(0, time.time() - self._start), self._duration), 2)

    def get_duration(self):
        return self._duration

    def stop(self):
        self._duration = None
        self._start = None
        self._base_time_nsecs = None
        logger.debug("stop")

    def is_playing(self):
        if self._duration is None:
            return False
        return self.get_position() < self._duration

    def close(self):
        self.stop()
