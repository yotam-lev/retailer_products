import threading
from typing import Any, Dict, Optional

class StateManager:
    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._state[key] = value

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            return self._state.get(key)

    def clear(self) -> None:
        with self._lock:
            self._state.clear()
