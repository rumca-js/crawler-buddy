from pathlib import Path
import shutil


class RepositoryInterface(object):
    def __init__(
        self, export_data, timeout_s=60 * 60, operating_dir=None, data_source_dir=None
    ):
        self.export_data = export_data
        self.timeout_s = timeout_s
        if not operating_dir:
            self.operating_dir = self.export_data.local_path
        else:
            self.operating_dir = operating_dir

        self.data_source_directory = data_source_dir

    def get_operating_dir(self):
        """
        repository path
        """
        if self.operating_dir:
            return Path(self.operating_dir)

    def get_local_dir(self):
        """
        local path within repository path (where operations on repository need to be made)
        """
        return self.get_operating_dir()

    def get_data_source_directory(self):
        """
        place where data are stored, needs to be copied to repository and pushed
        """
        if self.data_source_directory:
            return Path(self.data_source_directory)

    def push_to_repo(self, commit_message):
        # just copy from write directory, to local directory
        self.copy_tree()

    def clear_operating_directory(self):
        dir = self.get_operating_dir()
        if dir.exists():
            shutil.rmtree(dir)

    def copy_tree(self):
        expected_dir = self.get_local_dir()
        data_dir = self.data_source_directory

        if expected_dir != self.data_source_directory:
            shutil.copytree(data_dir, expected_dir, dirs_exist_ok=True)
