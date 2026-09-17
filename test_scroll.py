import subprocess
import time

print("Focus the PDF window now...")
time.sleep(5)

for i in range(10):
    subprocess.run([
        "ydotool",
        "mousemove", "-w", "-y", "-5"
    ])
    time.sleep(0.5)