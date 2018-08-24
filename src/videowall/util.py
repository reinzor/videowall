import argparse
import socket


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


def validate_ip_port(ip, port):
    try:
        socket.inet_pton(socket.AF_INET, ip)
    except socket.error as e:
        raise Exception(e)

    if not isinstance(port, int):
        raise Exception("Port should be an integer, current value: {}".format(port))


def validate_positive_int_argument(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue
