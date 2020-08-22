import os
import time
import stat
import math
from datetime import datetime
from typing import List
import shutil
import boto3


class CloudArchiver():

    SECONDS_PER_DAY = 86400
    ARCHIVE_S3_BUCKET_NAME = "pixi-cloud-archive"
    ARCHIVE_LOG_FILE = "archive.log"

    def __init__(self):
        self.access_threshold_days: int = 1

    def archive(self, archive_name: str, root_path: str, archive_path: str):
        shortlist = self._shortlist_archive_directory(root_path)
        archive_items = self._move_to_archive(shortlist, archive_path)
        self._move_files_to_s3(archive_name, archive_items)
        self._generate_archive_log(archive_name, root_path, archive_items)

    def _shortlist_archive_directory(self, root_path: str):

        # Shortlist paths to archive.
        paths = []
        archive_paths = []
        ignored_paths = []

        # Scan within this directory.
        all_paths = os.listdir(root_path)

        for partial_path in all_paths:
            path = os.path.join(root_path, partial_path)
            days_since_last_access = self._days_since_last_access(path)
            should_archive = days_since_last_access is not None and days_since_last_access >= self.access_threshold_days
            if should_archive:
                paths += self._filepaths_in(path)
                archive_paths.append(path)
            else:
                ignored_paths.append(path)

        # Return a list of all the paths we want to archive.
        self._print_paths_to_archive("Paths to ignore", root_path, ignored_paths)
        self._print_paths_to_archive("Paths to archive", root_path, archive_paths)

        return paths

    def _filepaths_in(self, path: str):
        # Get all file paths within this path.
        arr = []
        if os.path.isdir(path):
            for child in os.listdir(path):
                sub_path = os.path.join(path, child)
                arr += self._filepaths_in(sub_path)
        else:
            arr.append(path)
        return arr

    def _print_paths_to_archive(self, message:str, root_path: str, paths: List[str]):
        # Print in terminal the files we're about to archive.
        max_path_length = max(len(x) for x in paths)
        max_date_length = max(len(str(self._days_since_last_access(x))) for x in paths)
        gap_length = 8

        total_length = max(len(root_path), max_path_length + max_date_length + gap_length - len(root_path))
        
        print("\n" + "=" * total_length )
        print(message)
        print(root_path)
        print("=" * total_length + "\n")

        for path in paths:
            truncated_path = path.replace(root_path, ".")
            if os.path.isdir(path):
                truncated_path += "/*"
                
            day_str = f"{self._days_since_last_access(path)}d"
            gap_size = total_length - len(truncated_path) - len(day_str) 
            gap_str = " " * gap_size
            message = f"{truncated_path}{gap_str}{day_str}"
            print(message)

    def _days_since_last_access(self, path: str):
        # If this is a directory, the day of last access is the LATEST access date of all files in here.
        if os.path.isdir(path):
            latest_date = None
            for child in os.listdir(path):
                sub_path = os.path.join(path, child)
                sub_path_last_access = self._days_since_last_access(sub_path)

                if sub_path_last_access is None:
                    continue

                if latest_date is None or sub_path_last_access < latest_date:
                    latest_date = sub_path_last_access
            
            # Return the latest access date, or 0 if no files were found.
            return latest_date
        else:
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
        archive_items = []
        
        for path in paths:
            archive_key = self._create_archive_key(path)
            archive_key_path = os.path.join(archive_key, path)
            archive_file_path = os.path.join(archive_path, archive_key_path)

            archive_file_dir = os.path.dirname(archive_file_path)
            os.makedirs(archive_file_dir, exist_ok=True)

            shutil.move(path, archive_file_path)
            print(f"\nMoving file to archive:\n{path}\n{archive_file_path}")
            archive_items.append((archive_key_path, archive_file_path))
        
        return archive_items

    def _create_archive_key(self, path: str):
        file_stats_result = os.stat(path)
        access_time = file_stats_result[stat.ST_ATIME]
        access_date = datetime.fromtimestamp(access_time)
        key = os.path.join(str(access_date.year), str(access_date.month).zfill(2))
        return key

    def _move_files_to_s3(self, key_prefix: str, archive_items: list):
        # Upload everything under archive_path to S3.

        s3_client = boto3.client('s3')
        s3_client.create_bucket(Bucket=self.ARCHIVE_S3_BUCKET_NAME)

        try:
            for key, path in archive_items:
                key_with_prefix = f"{key_prefix}/{key}" 
                print(f"Uploading: {key_with_prefix}")
                s3_client.upload_file(path, self.ARCHIVE_S3_BUCKET_NAME, key_with_prefix)
            return True
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            return False

    def _generate_archive_log(self, archive_name: str, root_path: str, archive_items: list):
        # No items archived
        if len(archive_items) == 0:
            return

        date_str = datetime.now().isoformat()
        message = f"[{date_str}] {archive_name}: {len(archive_items)} items archived from {root_path}."
        print(message)

        with open(self.ARCHIVE_LOG_FILE, "a") as f:
            f.writelines(message + "\n")


def main():
    print("Running main from cloud archiver")
    pass


if __name__ == "__main__":
    main()
