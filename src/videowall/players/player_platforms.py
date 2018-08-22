from enum import Enum


class PlayerPlatform(Enum):
    X86_64 = "x86_64"
    RASPBERRY_PI = "raspberry_pi"

    def __str__(self):
        return self.value
