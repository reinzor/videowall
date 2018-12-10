import logging
import os

from .media_manager_exceptions import MediaManagerException

logger = logging.getLogger(__name__)


class MediaManager(object):
    def __init__(self, base_path, extensions=["mp4"]):
        real_base_path = os.path.realpath(os.path.expanduser(base_path))

        if not os.path.isdir(real_base_path):
            raise MediaManagerException("Specified base path %s does not exist", base_path)

        self._base_path = real_base_path
        self._extensions = extensions

    def _is_valid_extension(self, filename):
        return "." in filename and filename.split(".")[-1] in self._extensions

    def get_media_path(self):
        return self._base_path

    def get_full_path(self, filename):
        return os.path.join(self._base_path, filename)

    def get_filenames(self):
        return [filename for filename in os.listdir(self._base_path) if self._is_valid_extension(filename)]

    def get_extensions(self):
        return self._extensions
