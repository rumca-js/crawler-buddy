from pathlib import Path
import subprocess
import shutil
from utils.repositoryinterface import RepositoryInterface
from utils.logger import get_logger


class GitRepository(RepositoryInterface):
    def __init__(
        self, export_data, timeout_s=60 * 60, operating_dir=None, data_source_dir=None
    ):
        super().__init__(
            export_data,
            timeout_s,
            operating_dir=operating_dir,
            data_source_dir=data_source_dir,
        )

        self.git_repo = self.export_data.remote_path
        self.is_different_flag = None

    def push_to_repo(self, commit_message):
        repo_is_up = False
        try:
            self.up()
            repo_is_up = True
        except Exception as E:
            logger = get_logger("utils")
            logger.exc(
                E,
                "Cannot update repository, removing directory {}".format(
                    self.get_operating_dir()
                ),
            )
            self.clear_operating_directory()

        if repo_is_up:
            self.copy_tree()

            self.add([])
            if self.commit(commit_message) == 0:
                self.push()

                return True

    def get_local_dir(self):
        """
        TODO rename to repo dir
        """
        last = self.get_repo_name()
        return self.operating_dir / last

    def set_operating_dir(self, adir):
        """
        TODO rename to cwd dir
        """
        self.operating_dir = Path(adir)

    def up(self):
        cwd = self.get_operating_dir()
        local = self.get_local_dir()

        if not cwd.is_dir():
            cwd.mkdir(parents=True)

        if not local.is_dir():
            return self.clone()
        else:
            self.revert_all_changes()
            return self.pull()

    def add(self, files):
        p = subprocess.run(
            ["git", "add", "-A"],
            cwd=self.get_local_dir(),
            timeout=self.timeout_s,
            capture_output=True,
        )
        return self.check_process(p)

    def commit(self, commit_message):
        self.is_different_flag = self.is_different()

        if not self.is_different:
            return False

        p = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=self.get_local_dir(),
            timeout=self.timeout_s,
            capture_output=True,
        )
        return self.check_process(p)

    def push(self):
        if not self.is_different_flag:
            logger = get_logger("utils")
            logger.debug("Repository is not different")
            return False

        token = self.export_data.password
        user = self.export_data.user
        repo = self.get_repo_name()
        p = subprocess.run(
            [
                "git",
                "push",
                "https://{0}@github.com/{1}/{2}.git".format(token, user, repo),
            ],
            cwd=self.get_local_dir(),
            timeout=self.timeout_s,
            capture_output=True,
        )
        return self.check_process(p)

    def get_repo_name(self):
        if self.git_repo.endswith(".git"):
            last = Path(self.git_repo).parts[-1]
            last = Path(last)
            last = last.stem
        else:
            last = Path(self.git_repo).parts[-1]
            last = str(last)
        return last

    def clone(self):
        p = subprocess.run(
            ["git", "clone", self.git_repo],
            cwd=self.get_operating_dir(),
            timeout=self.timeout_s,
            capture_output=True,
        )
        return self.check_process(p)

    def is_different(self):
        p = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.get_local_dir(),
            timeout=self.timeout_s,
            capture_output=True,
        )

        text = p.stdout.decode().strip()

        if text == "":
            return False

        return True

    def revert_all_changes(self):
        p = subprocess.run(
            ["git", "checkout", "."],
            cwd=self.get_local_dir(),
            timeout=self.timeout_s,
            capture_output=True,
        )
        return self.check_process(p)

    def pull(self):
        p = subprocess.run(
            ["git", "pull"],
            cwd=self.get_local_dir(),
            timeout=self.timeout_s,
            capture_output=True,
        )
        return self.check_process(p)

    def check_process(self, p):
        if p.returncode != 0:
            logger = get_logger("utils")
            logger.error(
                "GIT status:{}\nstdout:{}\nstderr:{}".format(
                    p.returncode, p.stdout.decode(), p.stderr.decode()
                )
            )
        return p.returncode
