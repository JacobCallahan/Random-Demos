"""Allow multiple processes to communicate status on a single shared resource."""
import json
import time
from pathlib import Path
from uuid import uuid4
from broker.helpers import FileLock

class SharedResource:
    def __init__(self, resource_name, action, *action_args, **action_kwargs):
        self.resource_file = Path(f"/tmp/{resource_name}.shared")
        self.id = str(uuid4().fields[-1])
        self.action = action
        self.action_is_recoverable = action_kwargs.pop("action_is_recoverable", False)
        self.action_args = action_args
        self.action_kwargs = action_kwargs
        self.is_recovering = False

    def _update_status(self, status):
        with FileLock(self.resource_file):
            curr_data = json.loads(self.resource_file.read_text())
            curr_data["statuses"][self.id] = status
            self.resource_file.write_text(json.dumps(curr_data, indent=4))

    def _update_main_status(self, status):
        with FileLock(self.resource_file):
            curr_data = json.loads(self.resource_file.read_text())
            curr_data["main_status"] = status
            self.resource_file.write_text(json.dumps(curr_data, indent=4))

    def _check_all_status(self, status):
        with FileLock(self.resource_file):
            curr_data = json.loads(self.resource_file.read_text())
            for watcher_id in curr_data["watchers"]:
                if curr_data["statuses"].get(watcher_id) != status:
                    return False
            return True

    def _wait_for_status(self, status):
        while not self._check_all_status(status):
            time.sleep(1)

    def _wait_for_main_watcher(self):
        while True:
            curr_data = json.loads(self.resource_file.read_text())
            if curr_data["main_status"] != "done":
                time.sleep(30)
            elif curr_data["main_status"] == "action_error":
                self._try_take_over()
            elif curr_data["main_status"] == "error":
                raise Exception(f"Error in main watcher: {curr_data['main_watcher']}")
            else:
                break

    def _try_take_over(self):
        with FileLock(self.resource_file):
            curr_data = json.loads(self.resource_file.read_text())
            if curr_data["main_status"] in ("action_error", "error"):
                curr_data["main_status"] = "recovering"
                curr_data["main_watcher"] = self.id
                self.resource_file.write_text(json.dumps(curr_data, indent=4))
                self.is_main = True
                self.is_recovering = True
        self.wait()

    def register(self):
        print(f"Registering {self.id}")
        with FileLock(self.resource_file):
            if self.resource_file.exists():
                curr_data = json.loads(self.resource_file.read_text())
                self.is_main = False
            else:
                curr_data = {"watchers": [], "statuses": {}, "main_watcher": self.id, "main_status": "waiting"}
                self.is_main = True
            curr_data["watchers"].append(self.id)
            curr_data["statuses"][self.id] = "pending"
            self.resource_file.write_text(json.dumps(curr_data, indent=4))
        print(f"Registered {self.id}")

    def ready(self):
        self._update_status("ready")
        self.wait()

    def done(self):
        self._update_status("done")

    def act(self):
        try:
            self.action(*self.action_args, **self.action_kwargs)
        except Exception as err:
            self._update_main_status("error")
            raise err

    def wait(self):
        if self.is_main and not (self.is_recovering and not self.action_is_recoverable):
            self._wait_for_status("ready")
            self._update_main_status("acting")
            self.act()
            self._update_main_status("done")
        else:
            self._wait_for_main_watcher()

    def __enter__(self):
        self.register()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is FileNotFoundError:
            raise exc_value
        if exc_type is None:
            self.done()
            if self.is_main:
                self._wait_for_status("done")
                self.resource_file.unlink()
        else:
            self._update_status("error")
            if self.is_main:
                self._update_main_status("error")
            raise exc_value


def test_func():
    import random
    with SharedResource("my_resource", time.sleep, 60, action_is_recoverable=True) as resource:
        print(f"I got resource {resource.id}")
        print(f"Is main? {resource.is_main}")
        time.sleep(random.randint(1, 10))
        print(f"{resource.id} is ready")
        resource.ready()
        print(f"{resource.id} has come back from waiting")
    print(f"{resource.id} is done")

if __name__ == "__main__":
    import multiprocessing
    processes = []
    for i in range(5):
        p = multiprocessing.Process(target=test_func)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

