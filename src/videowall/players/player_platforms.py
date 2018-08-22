from .player_exceptions import PlayerException


class PlayerPlatform(object):
    pass


class PlayerPlatformX86(PlayerPlatform):
    pass


class PlayerPlatformRaspberryPi(PlayerPlatform):
    pass


_string_player_platform_map = {
  "x86": PlayerPlatformX86,
  "rpi": PlayerPlatformRaspberryPi
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


def get_player_platforms():
    return _string_player_platform_map.values()
