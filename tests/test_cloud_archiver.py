from src.cloud_archiver import CloudArchiver
import uuid
import os
import shutil
from datetime import datetime, timedelta


OUTPUT_PATH = "test_output"
SAMPLE_DATA_PATH = os.path.join(OUTPUT_PATH, "sample_data")
ARCHIVE_PATH = os.path.join(OUTPUT_PATH, "archive")

def setup_module():
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    os.makedirs(SAMPLE_DATA_PATH, exist_ok=True)
    os.makedirs(ARCHIVE_PATH, exist_ok=True)
    pass


def teardown_module():
    shutil.rmtree(OUTPUT_PATH)
    pass


def test_cloud_archiver():
    archiver = CloudArchiver()
    print("Testing cloud archiver")

    # Generate some files in the base directory.
    generate_test_files(5, SAMPLE_DATA_PATH)
    generate_test_files(5, SAMPLE_DATA_PATH, 3)

    # Generate a directory with some files.
    # This should NOT be archived.
    test_dir_1 = generate_directory(SAMPLE_DATA_PATH, "test_dir_1")
    generate_test_files(4, test_dir_1)
    generate_test_files(1, test_dir_1, 6)  # Even though these are old, the folder was touched recently.

    # Generate a directory. This one has no files, but has a nested dir with some old files.
    # These should be archived.
    test_dir_2 = generate_directory(SAMPLE_DATA_PATH, "test_dir_2")
    nested_dir_1 = generate_directory(test_dir_2, "nested_dir_1")
    generate_test_files(2, nested_dir_1, 6)

    archiver.archive("test-archive", SAMPLE_DATA_PATH, ARCHIVE_PATH)
    pass


def generate_directory(root_path: str, directory_name: str):
    directory_path = os.path.join(root_path, directory_name)
    os.makedirs(directory_path, exist_ok=True)
    return directory_path


def generate_test_files(n: int, root_path: str, days_old: int = 0):

    for _ in range(n):
        unique_id = uuid.uuid4().hex[:5]
        random_name = f"file_{unique_id}_{days_old}d.txt"
        file_path = os.path.join(root_path, random_name)
        with open(file_path, "w") as f:
            f.write("Random text file created for testing.")
        edit_date = datetime.now() - timedelta(days=days_old)
        os.utime(file_path, (edit_date.timestamp(), edit_date.timestamp()))
