@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo Compiling installer.py into a single executable...
pyinstaller --onefile --noconsole --name ROOT_Setup installer.py

echo.
echo Compilation Complete!
echo You can find your single executable in the "dist" folder.
echo You can send "dist\ROOT_Setup.exe" to your friend!
pause
