import socket

from videowall.util import to_dict

from .networking_exceptions import NetworkingException


class Message(object):
    def to_dict(self):
        return to_dict(self)

    def __repr__(self):
        return '{class_name}({params})'.format(
            class_name=self.__class__.__name__,
            params=', '.join('{}={}'.format(k, v) for k, v in vars(self).items()))


class VideocropConfig(Message):
    def __init__(self, bottom, left, right, top):
        self.bottom = int(bottom)
        self.left = int(left)
        self.right = int(right)
        self.top = int(top)

    @staticmethod
    def get_default():
        return VideocropConfig(0, 0, 0, 0)


class ClientConfig(Message):
    def __init__(self, videocrop_config):
        self.videocrop_config = VideocropConfig(**videocrop_config)

    @staticmethod
    def get_default():
        return ClientConfig(VideocropConfig.get_default().to_dict())


class ServerBroadcastMessage(Message):
    def __init__(self, filename, base_time, ip, clock_port, client_config):
        try:
            self.filename = filename
            self.base_time = int(base_time)
            self.ip = ip
            self.clock_port = int(clock_port)

            if not isinstance(client_config, dict):
                raise NetworkingException("The client config should be a dictionary")

            self.client_config = {}
            for ip, cfg in client_config.iteritems():
                if not isinstance(cfg, dict):
                    raise NetworkingException("Client config entry should be of dictionary")
                try:
                    socket.inet_pton(socket.AF_INET, ip)
                except socket.error as e:
                    raise NetworkingException(e)
                self.client_config[ip] = ClientConfig(**cfg)
        except Exception as e:
            raise NetworkingException(e)


class ClientBroadcastMessage(Message):
    def __init__(self, ip):
        self.ip = ip
