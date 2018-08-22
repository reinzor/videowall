from enum import Enum

from .player_exceptions import PlayerException


class PlayerPlatform(Enum):
    X86_64 = 1
    RASPBERRY_PI = 2


_string_player_platform_map = {
  "x86": PlayerPlatform.X86_64,
  "rpi": PlayerPlatform.RASPBERRY_PI
}


def player_platform_from_string(string):
    try:
        platform = _string_player_platform_map[string]
    except KeyError as e:
        raise PlayerException(e)
    else:
        return platform


def get_player_platform_strings():
    return _string_player_platform_map.keys()