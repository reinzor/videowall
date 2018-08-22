import gi
import logging.config

from client import Client
from server import Server

gi.require_version('Gst', '1.0')
gi.require_version('GstNet', '1.0')

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': "%(log_color)s[%(levelname)s] %(name)s: %(message)s",
        }
    },
    'handlers': {
        'stream': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
        },
    },
    'root': {
        'handlers': ['stream'],
        'level': 'INFO',
    },
})
