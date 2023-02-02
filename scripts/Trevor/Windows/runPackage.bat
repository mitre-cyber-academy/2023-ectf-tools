@echo off
call parameters.bat
cd /D %toolsPath%
@echo on

python3 -m ectf_tools run.package --name %sysName% --deployment %deplName% --package-out %packagePath% --package-name %packageName% --car-id %carID% --feature-number %featureNum%
pause