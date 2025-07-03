import time
import sys

print("Press Ctrl+C to stop the stopwatch.")
start_time = time.time()
try:
    while True:
        elapsed = time.time() - start_time
        sys.stdout.write(f"\rElapsed time: {elapsed:.2f} seconds")
        sys.stdout.flush()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nStopwatch stopped.")
