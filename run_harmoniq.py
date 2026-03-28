from __future__ import annotations
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

APP_PATH = Path(__file__).with_name("streamlit_app.py")
URL = "http://localhost:8501"

subprocess.Popen([
    sys.executable, "-m", "streamlit", "run", str(APP_PATH),
    "--server.headless", "true",
    "--browser.gatherUsageStats", "false"
])

time.sleep(3)
webbrowser.open(URL)
print(f"Harmoniq Studio is launching at {URL}")