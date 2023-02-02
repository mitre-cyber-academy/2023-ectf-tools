@echo off
call parameters.bat
cd /D %toolsPath%
@echo on

python3 -m ectf_tools device.load_hw --dev-in %carPath% --dev-name %carName% --dev-serial %serialPort%
pause
python3 -m ectf_tools device.bridge --bridge-id %carSocket% --dev-serial %serialPort%
pause
