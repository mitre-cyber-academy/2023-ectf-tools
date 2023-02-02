@echo off
call parameters.bat
cd /D %toolsPath%
@echo on

python3 -m ectf_tools run.unlock --car-bridge %carSerial% --host-tools %hostToolPath%

pause