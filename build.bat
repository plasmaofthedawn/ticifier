pyinstaller  --clean -c -F -n "ticgui.exe" --add-data "icon.ico;." -i "icon.ico" base.py
pyinstaller  --clean -w -F -n "ticnogui.exe" --add-data "icon.ico;." -i "icon.ico" base.py
