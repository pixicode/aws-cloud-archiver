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
    # shutil.rmtree(OUTPUT_PATH)
    pass


def test_cloud_archiver():
    archiver = CloudArchiver()
    print("Testing cloud archiver")
    generate_test_files(5, SAMPLE_DATA_PATH)
    generate_test_files(5, SAMPLE_DATA_PATH, 3)
    archiver.archive(SAMPLE_DATA_PATH, ARCHIVE_PATH)
    pass


def generate_test_files(n: int, root_path: str, days_old: int = 0):

    for _ in range(n):
        unique_id = uuid.uuid4().hex[:5]
        random_name = f"file_{unique_id}_{days_old}d.txt"
        file_path = os.path.join(root_path, random_name)
        with open(file_path, "w") as f:
            f.write("Random text file created for testing.")
        edit_date = datetime.now() - timedelta(days=days_old)
        os.utime(file_path, (edit_date.timestamp(), edit_date.timestamp()))
