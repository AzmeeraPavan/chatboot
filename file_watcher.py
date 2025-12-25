from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import indexing

ROW_DATA_PATH = r"C:\Users\azmee\rowdata" #here you the input data need to feed

class RowDataChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print("\n Change detected in rowData! Rebuilding vectorstore...\n")
        indexing.build_vectorstore()  # AUTO REBUILD

def start_watching(path=ROW_DATA_PATH):
    event_handler = RowDataChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(f" Watching folder: {path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
