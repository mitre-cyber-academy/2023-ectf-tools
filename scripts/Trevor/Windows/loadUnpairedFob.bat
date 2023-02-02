@echo off
call parameters.bat
cd /D %toolsPath%
@echo on

python3 -m ectf_tools device.load_hw --dev-in %fobPath% --dev-name %unpairName% --dev-serial %serialPort%
pause
python3 -m ectf_tools device.bridge --bridge-id %unpairSocket% --dev-serial %serialPort%
pause
