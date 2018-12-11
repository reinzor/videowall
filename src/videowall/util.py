import argparse
import base64
import netifaces as ni
import os
import re
import socket
import string


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


def validate_positive_float_argument(value):
    fvalue = float(value)
    if fvalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive float value" % value)
    return fvalue


def validate_ip_port(ip, port):
    validate_ip(ip)
    validate_positive_int_argument(port)
    return ip, port


def validate_positive_or_zero_int_argument(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive or zero int value" % value)
    return ivalue


def get_ifnames():
    return ni.interfaces()


def ip_from_ifname(ifname):
    return ni.ifaddresses(ifname)[ni.AF_INET][0]['addr']


def get_unique_filename(path):
    valid_chars = "-_/.%s%s" % (string.ascii_letters, string.digits)
    path = ''.join(c for c in path if c in valid_chars).replace(' ', '_')

    i = 0
    while os.path.exists(path):
        name, ext = os.path.splitext(path)
        s = re.search('(.*)_(\d+)\.', name)
        if s:
            name = s.group(1)
            i = int(s.group(2)) + 1
        path = "{}_{}{}".format(name, i, ext)
    return path
