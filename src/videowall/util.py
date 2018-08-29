import argparse
import socket
import fcntl
import struct


def to_dict(obj):
    """
    Convert object to dictionary, source:

    https://stackoverflow.com/questions/1036409/recursively-convert-python-object-graph-to-dictionary

    :param obj: Instance of a class
    :return: Object serialized to a dictionary
    """
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = to_dict(v)
        return data
    elif hasattr(obj, "_ast"):
        return to_dict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [to_dict(v) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, to_dict(value))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        return data
    else:
        return obj


def validate_ip(ip):
    try:
        socket.inet_pton(socket.AF_INET, ip)
    except socket.error as e:
        raise argparse.ArgumentTypeError(e)
    return ip


def validate_positive_int_argument(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def validate_ip_port(ip, port):
    validate_ip(ip)
    validate_positive_int_argument(port)
    return ip, port


def validate_positive_or_zero_int_argument(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive or zero int value" % value)
    return ivalue


def ip_from_ifname(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])
