import subprocess
import os
import logging
from pathlib import Path


class Wget(object):
    def __init__(self, url=None, cwd=None, timeout_s=60 * 60):
        self.url = url
        self.cwd = cwd
        self.timeout_s = timeout_s

    def download_all(self):
        cmds = ["wget", "-p", "-k", self.url]

        proc = subprocess.run(
            cmds, capture_output=True, cwd=self.cwd, timeout=self.timeout_s
        )

        if proc.returncode != 0:
            return None
