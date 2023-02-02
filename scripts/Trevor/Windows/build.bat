@echo off
call parameters.bat
cd /D %toolsPath%
@echo on

python3 -m ectf_tools build.env --design %designPath% --name %sysName%
python3 -m ectf_tools build.tools --design %designPath% --name %sysName%
python3 -m ectf_tools build.depl --design %designPath% --name %sysName% --deployment %deplName%

python3 -m ectf_tools build.car_fob_pair --design %designPath% --name %sysName% --deployment %deplName% --car-out %carPath% --fob-out %fobPath% --car-name %carName% --fob-name %pairName% --car-id %carID% --pair-pin %pairPIN%
python3 -m ectf_tools build.fob --design %designPath% --name %sysName%  --deployment %deplName% --fob-out %fobPath% --fob-name %unpairName%

@echo off
pause