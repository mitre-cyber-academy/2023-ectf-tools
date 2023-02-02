@echo off
call parameters.bat
cd /D %toolsPath%
@echo on

python3 -m ectf_tools device.load_hw --dev-in %fobPath% --dev-name %pairName% --dev-serial %serialPort%
pause
python3 -m ectf_tools device.bridge --bridge-id %pairSocket% --dev-serial %serialPort%
pause
