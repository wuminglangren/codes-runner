import subprocess
import os
import time
import signal
from datetime import datetime

current_working_directory = os.getcwd()
print(current_working_directory)

# Preserve commands in a list of string
commands = [
        "sleep 10",
        "sleep 10"
        ]

# Define the restricted time periods as a list of tuples (start_hour, start_minute, end_hour, end_minute)
restricted_periods = [
    ( 0, 59, 1, 20),    
    ( 4, 59, 5, 20),
    ( 8, 59, 9, 20),
    (16, 59,17, 20)
]

# Function to check if the current time is within any of the specified ranges
def is_time_to_stop(time_periods):
    current_time = datetime.now().time()
    for start_hour, start_minute, end_hour, end_minute in time_periods:
        start_time = datetime.strptime(f"{start_hour}:{start_minute}:00", "%H:%M:%S").time()
        end_time = datetime.strptime(f"{end_hour}:{end_minute}:00", "%H:%M:%S").time()
        if start_time <= current_time <= end_time:
            return True
    return False

# Loop through and run each command, checking the time before and during execution
for command in commands:
    while True:  # Repeat the loop until the command completes successfully
        try:
            # Run the command in a subprocess
            process = subprocess.Popen(
                command,                        # Command to run
                shell=True,                     # Use the shell to execute the command
                cwd=current_working_directory,  # Set the current working directory
                preexec_fn=os.setsid            # Create a new session so signals are managed correctly
            )

            # Monitor the command execution
            while process.poll() is None:  # Check if the process is still running
                if is_time_to_stop(restricted_periods):
                    os.killpg(os.getpgid(process.pid), signal.SIGSTOP)  # Pause the process group
                    print(f"Process paused due to time constraints: {command}")
                    while is_time_to_stop(restricted_periods):
                        print("Waiting for restricted time window to end...")
                        time.sleep(60)  # Wait for a minute before checking again
                    os.killpg(os.getpgid(process.pid), signal.SIGCONT)  # Resume the process group
                    print(f"Process resumed: {command}")
                time.sleep(1)  # Check every second (adjust as needed)

            # If the process completed successfully
            if process.poll() is not None and process.returncode == 0:
                print(f"Command {command} executed with return code {process.returncode}")
                break  # Exit the outer while loop to move to the next command
            else:
                print(f"Command {command} failed with return code {process.returncode}")

        except subprocess.CalledProcessError as e:
            print(f"Command {command} failed with return code {e.returncode}")

    time.sleep(1)  # Wait for 1 seconds before running the next command (adjust as needed)

