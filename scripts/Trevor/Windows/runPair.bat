@echo off
call parameters.bat
cd /D %toolsPath%
@echo on

python3 -m ectf_tools run.pair --name %sysName% --unpaired-fob-bridge %unpairSocket% --paired-fob-bridge %pairSocket% --pair-pin %pairPIN%
pause