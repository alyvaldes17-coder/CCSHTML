import threading
import time
from core.states import AccountState


class Supervisor:
    def __init__(self, manager, heartbeat_timeout: float = 1.0, interval: float = 0.1):
        self.manager = manager
        self.heartbeat_timeout = heartbeat_timeout
        self.interval = interval
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        t = threading.Thread(target=self._loop, daemon=True)
        self._thread = t
        t.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)

    def _loop(self):
        while not self._stop.is_set():
            now = time.time()
            for name, acc in list(self.manager.accounts.items()):
                # Launch browser-based worker when configured
                try:
                    use_browser = getattr(acc, "use_browser", False)
                except Exception:
                    use_browser = False

                # Evitar crear thread si ya hay uno activo
                if acc.thread is not None and acc.thread.is_alive():
                    continue

                if acc.state == AccountState.RUNNING and use_browser:
                    # spawn AccountWorker in a new thread
                    from worker.account_worker import AccountWorker
                    worker = AccountWorker(acc)
                    t = threading.Thread(target=worker.run, daemon=True)
                    acc.thread = t
                    t.start()

                # Existing heartbeat checks for runtime workers
                if acc.state in (AccountState.RUNNING, AccountState.PAUSED) and not (use_browser and acc.thread is not None):
                    if acc.last_heartbeat is None or (now - acc.last_heartbeat) > self.heartbeat_timeout:
                        acc.state = AccountState.ERROR
            time.sleep(self.interval)
