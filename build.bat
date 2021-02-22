pyinstaller -c -F -n "ticgui"   --add-data "icon.ico;." --add-data "disabled.ico;." --noconfirm -i "icon.ico" base.py
pyinstaller -w -F -n "ticnogui" --add-data "icon.ico;." --add-data "disabled.ico;." --noconfirm -i "icon.ico" base.py
