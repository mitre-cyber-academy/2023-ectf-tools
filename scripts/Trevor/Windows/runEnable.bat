@echo off
call parameters.bat
cd /D %toolsPath%
@echo on

python3 -m ectf_tools run.enable --name %sysName% --fob-bridge %enableSocket% --package-in %packagePath% --package-name %packageName%
pause