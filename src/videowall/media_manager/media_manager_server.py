import logging
import multiprocessing
import os
import subprocess
import time
from functools import partial

from .media_manager import MediaManager

logger = logging.getLogger(__name__)


def _rsync(local_path, remote_path):
    cmd = 'rsync -avzP {} {}'.format(local_path, remote_path)
    logger.debug('rsync command: %s', cmd)
    t_start = time.time()
    with open(os.devnull, 'w') as DEVNULL:
        subprocess.call(
            cmd.split(' '),
            stdout=DEVNULL,
            stderr=subprocess.STDOUT
        )
    logger.debug('rsync to remote path %s took %.3f seconds', remote_path, time.time() - t_start)


class MediaManagerServer(MediaManager):
    def __init__(self, base_path, num_sync_processes=10):
        super(MediaManagerServer, self).__init__(base_path)
        self._num_sync_processes = num_sync_processes

    def _sync_many(self, remote_paths):
        logger.info('rsync to remote paths %s', remote_paths)

        t_start = time.time()
        pool = multiprocessing.Pool(processes=self._num_sync_processes)
        pool.map(partial(_rsync, self._base_path), remote_paths)
        logger.info('rsync to %d remotes with %d processes took %.3f seconds',
                    len(remote_paths), self._num_sync_processes, time.time() - t_start)

    def sync(self, remote_path):
        if isinstance(remote_path, list):
            remote_paths = remote_path
        else:
            remote_paths = [remote_path]

        self._sync_many(remote_paths)
