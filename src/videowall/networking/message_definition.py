class Message(object):
    def to_dict(self):
        return {k: v for k, v in vars(self).items()}

    def __repr__(self):
        return '{class_name}({params})'.format(
            class_name=self.__class__.__name__,
            params=', '.join('{}={}'.format(k, v) for k, v in self.to_dict().iteritems()))


class BroadcastMessage(Message):
    def __init__(self, filename, base_time, position, duration, player_ip, player_port, seek_lookahead):
        self.filename = filename
        self.base_time = int(base_time)
        self.position = int(position)
        self.duration = int(duration)
        self.player_ip = player_ip
        self.player_port = int(player_port)
        self.seek_lookahead = int(seek_lookahead)
