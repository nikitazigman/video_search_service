import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent


class FileReplacerEventHandler(FileSystemEventHandler):

    def on_created(self, event: FileCreatedEvent) -> None:
        """Files deletion and creation will be handled via create event"""

    def on_modified(self, event: FileModifiedEvent) -> None:
        """Files modification will be handled via modification event"""


def observe_folder(folder_path: str) -> None:
    observer = Observer()
    observer.schedule(
        event_handler=FileReplacerEventHandler(),
        path=folder_path,
        recursive=True
    )
    observer.start()

    try:
        while True:
            time.sleep(0.1)
    finally:
        observer.stop()
        observer.join()
