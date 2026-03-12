
import subprocess
import time


# command = ["poetry", "run", "python", "script_server.py", "-k", "-m", "--trace"]
command = ["poetry", "run", "python", "script_server.py", "-k", "-m"]


def run_forever():
    while True:
        try:
            print("Starting script")
            process = subprocess.Popen(command)
            return_code = process.wait()
            print(f"Process exited with code {return_code}. Restarting...")
        except KeyboardInterrupt:
            print("Runner stopped by user.")
            return
        except Exception as E:
            print(f"Error {e}. Restarting...")


if __name__ == "__main__":
    run_forever()
