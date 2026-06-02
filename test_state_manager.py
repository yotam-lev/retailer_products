import threading
import time
import random
from src.state_manager import StateManager

def worker(sm, key, value):
    sm.set(key, value)
    time.sleep(random.uniform(0.001, 0.01))
    sm.get(key)

def test_state_manager_thread_safety():
    sm = StateManager()
    threads = []
    for i in range(100):
        t = threading.Thread(target=worker, args=(sm, f"key_{i}", i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Thread safety test passed.")

if __name__ == "__main__":
    test_state_manager_thread_safety()
