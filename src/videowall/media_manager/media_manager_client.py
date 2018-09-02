import logging

from .media_manager import MediaManager

logger = logging.getLogger(__name__)


class MediaManagerClient(MediaManager):
    def __init__(self, base_path):
        super(MediaManagerClient, self).__init__(base_path)
