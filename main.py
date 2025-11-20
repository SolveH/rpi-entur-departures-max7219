import argparse
import os
import signal
import sys

from display_departures import display_next_departures_on_max7219  # and any other needed symbols

PID_FILE = "/tmp/rutetider.pid"


def start():
    pid = os.fork()
    if pid > 0:
        # Parent process: write child PID and exit
        with open(PID_FILE, "w") as f:
            f.write(str(pid))
        print("Started with PID", pid)
        sys.exit(0)
    sys.stdout = open("/tmp/rutetider.log", "a", buffering=1)
    sys.stderr = open("/tmp/rutetider.log", "a", buffering=1)
    print("Child process started", flush=True)
    display_next_departures_on_max7219()


def stop():
    if not os.path.exists(PID_FILE):
        print("Not running.")
        return
    with open(PID_FILE) as f:
        pid = int(f.read())
    try:
        os.kill(pid, signal.SIGTERM)
        print("Stopped process", pid)
    except ProcessLookupError:
        print("Process not found.")
    os.remove(PID_FILE)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["start", "stop"])
    args = parser.parse_args()

    if args.command == "start":
        start()
    elif args.command == "stop":
        stop()
