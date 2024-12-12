import subprocess
import os


class FFmpeg(object):
    def __init__(self, name, cwd=None, timeout_s=60 * 60):
        self.name = name
        self.timeout_s = timeout_s
        self.cwd = cwd

    def convert_to_mp3(self, mp3_name):
        data = subprocess.run(
            ["ffmpeg", "-y", "-i", self.name, "-vn", mp3_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.cwd,
            timeout=self.timeout_s,
        )

        os.remove(self.name)

        return mp3_name

    def get_mp3_file_name(self):
        return self.name.replace(".m4a", ".mp3")

    @staticmethod
    def validate():
        try:
            proc = subprocess.run(
                ["ffmpeg"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
            )
        except:
            return False
        return True


class Vlc(object):
    def __init__(self, name):
        self.name = name

    def run(self):
        data = subprocess.run(
            ["vlc", self.name, "vlc://quit"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.cwd,
            timeout=self.timeout_s,
        )

    @staticmethod
    def validate():
        try:
            proc = subprocess.run(
                ["vlc"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
            )
        except:
            return False
        return True
