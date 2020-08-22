import os
import time
import stat
import math
from datetime import datetime
from typing import List
import shutil


class CloudArchiver():

    SECONDS_PER_DAY = 86400

    def __init__(self):
        self.access_threshold_days: int = 1
        pass

    def archive(self, root_path: str, archive_path: str):
        shortlist = self._shortlist_archive_directory(root_path)
        self._print_paths_to_archive(shortlist)
        self._move_to_archive(shortlist, archive_path)
        pass

    def _shortlist_archive_directory(self, root_path: str):

        # Shortlist paths to archive.
        paths = []

        # Scan within this directory.
        all_paths = os.listdir(root_path)

        for partial_path in all_paths:
            path = os.path.join(root_path, partial_path)
            should_archive = self._days_since_last_access(path) >= self.access_threshold_days
            if should_archive:
                paths.append(path)

        # Return a list of all the paths we want to archive.
        return paths

    def _print_paths_to_archive(self, paths: List[str]):
        # Print in terminal the files we're about to archive.
        max_path_length = max(len(x) for x in paths)
        max_date_length = max(len(str(self._days_since_last_access(x))) for x in paths)
        gap_length = 4

        total_length = max_path_length + max_date_length + gap_length
        
        print("\n" + "=" * total_length )
        print("Paths to Archive")
        print("=" * total_length + "\n")

        for path in paths:
            day_str = f"{self._days_since_last_access(path)}d"
            gap_size = total_length - len(path) - len(day_str) 
            gap_str = " " * gap_size
            message = f"{path}{gap_str}{day_str}"
            print(message)

    def _days_since_last_access(self, path: str):
        file_stats_result = os.stat(path)
        access_time = file_stats_result[stat.ST_ATIME]
        access_delta_seconds = time.time() - access_time
        access_delta_days = self._convert_seconds_to_days(access_delta_seconds)
        return access_delta_days

    def _convert_seconds_to_days(self, seconds: float):
        return math.floor(seconds / self.SECONDS_PER_DAY)

    def _move_to_archive(self, paths: List[str], archive_path: str):
        # Ensure that the archive folder exists.
        os.makedirs(archive_path, exist_ok=True)

        for path in paths:
            archive_key = self._create_archive_key(path)
            archive_key_path = os.path.join(archive_path, archive_key)
            archive_file_path = os.path.join(archive_key_path, path)

            archive_file_dir = os.path.dirname(archive_file_path)
            os.makedirs(archive_file_dir, exist_ok=True)

            shutil.move(path, archive_file_path)
            print(f"Moving {path} to {archive_file_path}")

    def _create_archive_key(self, path: str):
        file_stats_result = os.stat(path)
        access_time = file_stats_result[stat.ST_ATIME]
        access_date = datetime.fromtimestamp(access_time)
        key = os.path.join(str(access_date.year), str(access_date.month).zfill(2))
        return key


def main():
    print("Running main from cloud archiver")
    pass


if __name__ == "__main__":
    main()
