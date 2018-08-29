import logging
import os
import subprocess

from videowall.networking import NetworkingClient
from videowall.networking.message_definition import ClientConfig
from videowall.players import PlayerClient
from videowall.players.player_platforms import string_from_player_platform

logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, ip, player_platform, broadcast_port):
        self._networking = NetworkingClient(ip, broadcast_port)
        self._player = PlayerClient(player_platform)

    @staticmethod
    def _get_client_specific_config(ip, client_config):
        if ip in client_config:
            return client_config[ip]
        logging.warn("%s not present in client_config %s, using default config", ip, client_config)
        return ClientConfig.get_default()

    def run(self):
        while True:
            msg = self._networking.receive_broadcast()
            client_cfg = Client._get_client_specific_config(self._networking.get_ip(), msg.client_config)

            self._player.play(msg.filename, msg.base_time, msg.ip, msg.clock_port, client_cfg.videocrop_config)

    def close(self):
        self._player.close()


class ClientSubprocess(object):
    def __init__(self, ip, player_platform, broadcast_port):
        self._networking = NetworkingClient(ip, broadcast_port)
        self._player_platform = player_platform

        self._player_client_executable = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../scripts",
                                                      "player_client")
        print self._player_client_executable
        self._sub_process = None

    def run(self):
        while True:
            msg = self._networking.receive_broadcast()
            # client_cfg = self._get_client_specific_config(msg.client_config)

            if self._sub_process:
                self._sub_process.terminate()

            player_client_executable = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "../../scripts", "player_client")
            cmd = "{executable} --ip {ip} --port {port} {player_platform} {filename} {base_time}".format(
                executable=player_client_executable,
                ip=msg.ip,
                port=msg.clock_port,
                player_platform=string_from_player_platform(self._player_platform),
                filename=msg.filename,
                base_time=msg.base_time
            )
            print "Cmd:", cmd

            self._sub_process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)

    def close(self):
        if self._sub_process:
            self._sub_process.terminate()
