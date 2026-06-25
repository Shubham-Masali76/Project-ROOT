@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo Compiling bootstrapper.py into a single executable...
pyinstaller --onefile --noconsole --name ROOT_Setup bootstrapper.py

echo.
echo Compilation Complete!
echo You can find your single executable in the "dist" folder.
echo You can send "dist\ROOT_Setup.exe" to your friend!
pause
