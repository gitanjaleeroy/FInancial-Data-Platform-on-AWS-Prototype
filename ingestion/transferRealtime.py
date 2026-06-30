import time
import os
import boto3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_FOLDER = r"<folder>"
BUCKET = "testbucket"
PREFIX = "raw/"

s3 = boto3.client("s3")

def to_s3_key(full_path):
    # get path relative to base folder
    rel_path = os.path.relpath(full_path, WATCH_FOLDER)

    # normalize Windows slashes to S3 style
    rel_path = rel_path.replace("\\", "/")

    return PREFIX + rel_path


def upload(file_path):
    if not os.path.isfile(file_path):
        return

    # wait briefly so file finishes writing
    time.sleep(1)

    key = to_s3_key(file_path)

    print(f"Uploading {file_path} -> s3://{BUCKET}/{key}")
    s3.upload_file(file_path, BUCKET, key)


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        upload(event.src_path)


if __name__ == "__main__":
    observer = Observer()
    observer.schedule(Handler(), WATCH_FOLDER, recursive=True)
    observer.start()

    print("Watching:", WATCH_FOLDER)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()