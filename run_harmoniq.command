#!/bin/bash
read -p "Paste the folder path where streamlit_app.py is located: " APPDIR
if [ -z "$APPDIR" ]; then exit 1; fi
if [ ! -f "$APPDIR/streamlit_app.py" ]; then
  osascript -e 'display dialog "streamlit_app.py was not found in that folder." buttons {"OK"} default button "OK"'
  exit 1
fi
osascript <<EOF
tell application "Terminal"
    activate
    do script "cd \"$APPDIR\" && python3 -m streamlit run streamlit_app.py"
end tell
EOF
sleep 5
open -a "Google Chrome" "http://localhost:8501"
exit 0