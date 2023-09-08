import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileObserverHandler(FileSystemEventHandler):

    def __init__(self, shared_file_abspath, notify_function):
        self.shared_file_abspath = shared_file_abspath
        self.notify_function = notify_function

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path == self.shared_file_abspath:
            self.notify_function(event)


if __name__ == "__main__":
    shared_file = os.path.abspath("shared_file.txt")

    def notify_on_modified(event):
        print(f"notify_on_modified : {event}")


    file_observer_handler = FileObserverHandler(shared_file, notify_on_modified)
    print(file_observer_handler)
    observer = Observer()
    observer.schedule(file_observer_handler, path=os.path.dirname(shared_file), recursive=False)
    observer.start()

    print(f"try to modify :", shared_file)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
