# 2023 MITRE eCTF Tools: Protected Automotive Remote Entry Device (PARED)
This repository contains tools to run MITRE's 2023 Embedded System CTF
(eCTF) design - see https://ectf.mitre.org/ for details.

**Nothing in this repository should be modified in your design**.

# Environment Setup

**Required Software**
- Git
- Docker
- Python
- Stellaris ICDI Drivers
- UNIFLASH

**Recommended Software**
- Visual Studio Code
  - Python, C/C++, Cortex-Debug Extensions
- OpenOCD
- ARM GNU Toolchain

## Required Software

The following sections detail how to install the required software for this competition.

### Package Managers

It is important to note that some of these requirements can be installed via a package manager, and some of the install pages actually recommend it. A package manager is like an Appstore for your computer that runs on the commandline.

NOTE: Package managers are not required and these tools can be installed through other means. Skip ahead if you wish to use other methods.

Using a package manager can make the install process easier.

To find the proper package name you can just search `<package manager> <software name> install` in your web browser.

But first you need to install the proper package manager.

**Windows: Chocolatey**

Chocolatey is a package manager that can be installed on Windows. It has packages for most of the software you will need for eCTF.

[https://docs.chocolatey.org/en-us/choco/setup](https://docs.chocolatey.org/en-us/choco/setup)

**Mac: Homebrew**

Homebrew is a preferred package manager for MacOS devices. It has install candidates for most of the software. It is even the prefered install method for some of the packages such as `git`.

[https://brew.sh/](https://brew.sh/)

**Ubuntu: apt**

Linux, uses package managers by default. APT, or a different package manager, should already be installed on your system.

[https://manpages.ubuntu.com/manpages/trusty/en/man8/apt.8.html](https://manpages.ubuntu.com/manpages/trusty/en/man8/apt.8.html)

### Git
Git is an open-source version control system. It will allow your team to collaborate on a single code base while managing a history of all the changes you make.

Git is required to submit your design for testing and progression to the Attack Phase. This makes it easy for the organizers to download your code for testing and allows your team to tag a specific version of your code you want to submit.

**All Platforms**
[https://git-scm.com/downloads](https://git-scm.com/downloads)

### Docker
Docker is a lightweight containerization system. It allows you to package all your tools with the software required to run them.

Docker is used in the eCTF to create an environment for your host tools to execute in. This allows teams to use different programming languages, tools, or libraries during the Design Phase without requiring other teams to download additional software to use their design. Instead, each team will deliver a Dockerfile that builds an image capable of running all their tools.

**All Platforms**
[https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)

### Python
Python is a highly readable language with substantial support, which makes it easy to get started with powerful development capability. Setting up a Python virtual environment makes it easy to handle dependencies. Python is used in the eCTF tools repository we provide, as well as our reference design example. The reference design requires Python 3.7 or above.

**All Platforms**
There are many methods to install python on your system
- python.org: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- pyenv: [https://github.com/pyenv/pyenv](https://github.com/pyenv/pyenv)
- other: [https://realpython.com/installing-python/](https://realpython.com/installing-python/)

### Stellaris ICDI Drivers
The development board we will use for this competition is the Texas Instruments TM4C123G LaunchPad Evaluation Kit. You can find a lot of helpful resources on the product page at [https://www.ti.com/tool/EK-TM4C123GXL](https://www.ti.com/tool/EK-TM4C123GXL).

The board has an integrated In-Circuit Debug Interface (ICDI). This is what is used to support programming and debugging of the hardware. To use it you need to install the correct drivers.

**All Platforms**
[https://www.ti.com/tool/STELLARIS_ICDI_DRIVERS](https://www.ti.com/tool/STELLARIS_ICDI_DRIVERS)

### UNIFLASH
To program the flash memory on the development board, you need to download a programmer. UNIFLASH is compatible with Windows, MacOS, and Linux. There is also an LMFLASHPROGRAMMER, but it has export restrictions and is only compatible with Windows.

**All Platforms**
[https://www.ti.com/tool/UNIFLASH](https://www.ti.com/tool/UNIFLASH)

## Recommended Software
The following sections detail how to install the recommended software for this competition.

### ARM GNU Toolchain
Our custom build process for the embedded software that will be loaded onto the TI board will run in a Docker container. Therefore, it is not necessary to install a compiler on your local machine. However, it may be helpful to have if you want to do any local builds of your code or debug any build issues. A popular cross-compilation toolchain for ARM is the GNU Toolchain.

**All Platforms**
[https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads)

### Open OCD
Open On-Chip Debugger (OpenOCD) is an open-source tool that supports debugging through a JTAG interface on many development boards. OpenOCD can be used with the Cortex-Debug extension in Visual Studio Code to provide an interactive debugging environment for the Texas Instrument development board we will use.

**All Platforms**
[https://openocd.org/pages/getting-openocd.html](https://openocd.org/pages/getting-openocd.html)

**Usage**
Open OCD can be used with gdb (arm-none-eabi-gdb from the ARM GNU Toolchain) or it can be used with the Cortex-Debug extension in Visual Studio Code (instructions in following section). To use Open OCD without Visual Studio Code, do the following:
1. In a terminal, start Open OCD with `openocd -f interface/ti-icdi.cfg -f board/ti_ek-tm4c123gxl.cfg`.
2. In another terminal, start GDB with `arm-none-eabi-gdb <elf file path> -ex "target extended-remote localhost:3333"`

### Visual Studio Code
While there are many good IDEs, we recommend using Visual Studio Code (VSCode) because of its support for in-IDE debugging through the Cortex-Debug extension. Additionally, it is easier to setup than other IDEs we have used.

**All Platforms**
[https://code.visualstudio.com/download](https://code.visualstudio.com/download)

#### Extensions
Extensions can be added to Visual Studio Code to add features that make it feel more like an IDE than a text editor. There are three extensions that we recommend.
- Python
- C/C++
- Cortex-Debug

**All Platforms**
[https://code.visualstudio.com/docs/editor/extension-marketplace](https://code.visualstudio.com/docs/editor/extension-marketplace)

##### Cortex-Debug
To configure Visual Studio Code with the Cortex-Debug extension and OpenOCD, you will need to create a launch configuration in Visual Studio Code that tells the extension information about your debug session such as the source code location, the path to your OpenOCD executable, and the board configuration files for OpenOCD to use.

In your design repository, an example debug launch configuration could look like this:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Cortex Debug",
            "cwd": "${workspaceFolder}",
            "executable": "${workspaceRoot}/path/to/application.elf",
            "armToolchainPath": "/path/to/arm-none-eabi/bin",
            "request": "launch",
            "type": "cortex-debug",
            "runToEntryPoint": "main",
            "servertype": "openocd",
            "device": "TM4C123GH6PM",
            "configFiles": [
                "interface/ti-icdi.cfg",
                "board/ti_ek-tm4c123gxl.cfg"
            ],
            "svdFile": "${workspaceRoot}/debug/TM4C123GH6PM.svd"
        }
    ]
}
```

## eCTF Tools Setup

Once you have Git, Docker, and python3 installed, you need to clone this tools repo and install it as a python package. We recommend using a [python virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)
when installing packages for this competition. With your virtual environment activated, run the following:

```shell
git clone <Copy of this repo URL>
python3 -m pip install -e <path to cloned repo>
```

You must also clone the insecure example repository.

## Hardware Setup
To prepare your hardware for the eCTF competition, you will need to install a bootloader (written by the organizers) on the development boards. Additionally, for the design to function the boards need to be connected over a shared UART interface.

### Custom Bootloader
Using UNIFLASH, you should load the bootloader found in this repository (bootloader/bootloader.bin) onto the Tiva development boards. The version found here is used for the Design Phase, and will be used to load your designs onto the board. During the Attack Phase, a functionally equivalent version will be used to load other teams' designs.

### UART
The two Tiva development boards needs to be connected over a shared UART interface.
The boards should be connected as follows:

| TM4C123G Pin | TM4C123G Pin |
| :---         | :---         |
| GND          | GND          |
| PB0          | PB1          |
| PB1          | PB0          |

# Using the eCTF Tools Repository

### Getting Debug Information

When running any of the steps below, you can provide `--debug` between the
`ectf_tools` and `<phase>.<step>` portions of the command. For example:

```shell
python3 -m ectf_tools --debug build.env --design <PATH_TO_DESIGN> --name <SYSTEM_NAME>
```

### 1. Build
There are four stages to the build process. Each stage produces a functional
part of the system, whether it be an execution environment, system-wide secrets,
devices, or host tools.

#### 1a. `build.env`
```shell
python3 -m ectf_tools build.env --design <PATH_TO_DESIGN> --name <SYSTEM_NAME>
```

This builds a Docker image that will be used to create build and run
environments for the system. Each subsequent step will be run in temporary
containers, where all inputs are provided via read-only volumes, and outputs are
stored on writable volumes. The environment build step will only be run once
ever and **the resulting image will be distributed to teams**.

During development, you only need to change this whenever you need to
change the environment (e.g., adding a package).

This step will build a docker container based on the Dockerfile in the design
repo.

#### 1b. `build.tools`
```shell
python3 -m ectf_tools build.tools --design <PATH_TO_DESIGN> --name <SYSTEM_NAME>
```

This step creates a volume containing host tools that will be used when running
the system. You must pass the path to the design repo as an argument, and the
eCTF tools will invoke your host tools makefile. In the insecure example, the
host tools are simply copied to the output volume as they are implemented in
python scripts and do not need to be compiled.

#### 1c. `build.depl`
```shell
python3 -m ectf_tools build.depl --design <PATH_TO_DESIGN> --name <SYSTEM_NAME> --deployment <DEPLOYMENT_NAME>
```

This step generates system-wide secrets for a specific instance of the system
(i.e., a deployment). The eCTF tools will invoke the design deployment Makefile,
where secrets can be stored on a specific output volume.

#### 1d. `build.car_fob_pair`
```shell
python3 -m ectf_tools build.car_fob_pair --design <PATH_TO_DESIGN> --name <SYSTEM_NAME> --deployment <DEPLOYMENT_NAME> --car-out <CAR_OUTPUT_FOLDER> --fob-out <FOB_OUTPUT_FOLDER> --car-name <CAR_BINARY_NAME> --fob-name <FOB_BINARY_NAME> --car-id <CAR_ID> --pair-pin <FOB_PAIR_PIN>
```

This step builds car and pre-paired fob binaries that can be loaded into the
development boards. The eCTF tools will invoke the design device Makefile in the
appropriate folder, which places the firmware binary and EEPROM contents in an
output volume. This step also packages the firmware and EEPROM contents together
so they can be loaded into the device.

#### 1d. `build.fob`
```shell
python3 -m ectf_tools build.fob --design <PATH_TO_DESIGN> --name <SYSTEM_NAME> --deployment <DEPLOYMENT_NAME> --fob-out <FOB_OUTPUT_FOLDER> --fob-name <FOB_BINARY_NAME>
```

This step builds an unpaired fob binary that can be loaded into the
development board. The eCTF tools will invoke the design device Makefile in the
`fob` folder, which places the firmware binary and EEPROM contents in an
output volume. This step also packages the firmware and EEPROM contents together
so they can be loaded into the device.


### 2. Load and Launch Device

Follow these steps load binaries onto a device and open a connection for the
host tools.

#### 2a. `device.load_hw`

The load stage loads a packaged device binary+EEPROM into a target device. The
`build.car_fob_pair` and `build.fob` steps must already have been run before
running this step.

Plug a device with the bootloader installed into your computer, and hold down
the right button while turning on the power. The device will slowly flash a
cyan LED, indicating it is ready to install firmware. Figure out the serial port
in your computer that the board is connected to (windows device manager or
linux/mac `dmesg`), then start the device load step:

```shell
python3 -m ectf_tools device.load_hw --dev-in <DEVICE_ARTIFACTS_FOLDER> --dev-name <DEVICE_BINARY_NAME> --dev-serial <SERIAL_PORT>
```

When the install finishes, the cyan LED will be solid. Now, power cycle the
device, and the LED should be solid green, showing that the firmware is running.


#### 2b. `device.bridge`
```shell
python3 -m ectf_tools device.bridge --bridge-id <INET_SOCKET> --dev-serial <SERIAL_PORT>
```

The device bridge step launches a connection between a specific serial port
(for a device) and an INET socket (for the host tools). This step will actively
run in a terminal window, so you should open a separate window for this step.
The bridge must be running for the host tools to interact with the device.

### 3. Run

#### 3a. `run.unlock`
```shell
python3 -m ectf_tools run.unlock --name <SYSTEM_NAME> --car-bridge <CAR_SOCKET>
```

This run step invokes the unlock host tool, which connects to a car to receive messages over UART.

#### 3b. `run.pair`
```shell
python3 -m ectf_tools run.pair --name <SYSTEM_NAME> --unpaired-fob-bridge <UNPAIRED_FOB_SOCKET> --paired-fob-bridge <PAIRED_FOB_SOCKET> --pair-pin <PAIR_PIN>
```

The run step invokes the pair host tool, which connects to a paired fob and an unpaired fob.


#### 3c. `run.package`
```shell
python3 -m ectf_tools run.package --name <SYSTEM_NAME> --deployment <DEPLOYMENT_NAME> --package-out <PACKAGE_OUT> --package-name <PACKAGE_NAME> --car-id <CAR_ID> --feature-number <FEATURE_NUMBER>
```

This run step invokes the package host tool, which generates a package file
with name package-name in the directory package-out. This step utilizes the inputs
car-id and feature-number as well as shared secrets to generate a package.

#### 3d. `run.enable`
```shell
python3 -m ectf_tools run.enable --name <SYSTEM_NAME> --fob-bridge <FOB_SOCKET> --package_in <PACKAGE_IN> --package_name <PACKAGE_NAME>
```

This run step invokes the enable host tool, which reads in a previously created
feature package and enables that feature on the connected fob.

# Additional Tips

### Docker
To view all running Docker containers:
```shell
docker ps
```

To kill the Docker container with process ID 12345:
```shell
docker kill 12345
```

To kill all Docker containers:
```shell
docker kill $(docker ps -q)
```
You can streamline this by adding `alias dockerka='docker kill $(docker ps -q)'` to your `.bashrc`.

To run a command in the Docker container `test:deployment`:
```shell
docker run test:deployment echo "this echo command will be run in the container"
```

Docker can chew up disk space, so if you need to reclaim some, first clean up unused
containers and volumes
```shell
docker container prune
docker volume prune
```

If that isn't enough, you can clean up all containers and volumes:
```shell
docker container prune -a
docker volume prune -a
```
NOTE: these will remove all of the cached containers, so the next builds may take a longer time

These are some helpful commands to have handy when managing your docker state:

- **Kill all docker containers**: `docker kill $(docker ps -q)`
- **Kill the process in your window**: `CTRL-C`
- **Suspend the process in your window**: `CTRL-Z`
  - **Note:** Make sure to kill the process after!

### udev Rules (Linux Only)
It is helpful to create custom udev rules for the Tiva boards used in the competition.
This allows for static naming between board resets. These should be placed in:
/etc/udev/rules.d/10-local.rules

```
ACTION=="add", ATTRS{idVendor}=="1cbe", ATTRS{idProduct}=="00fd", ATTRS{serial}=="0E2340C0", SYMLINK+="board_2"
ACTION=="add", ATTRS{idVendor}=="1cbe", ATTRS{idProduct}=="00fd", ATTRS{serial}=="0E235955", SYMLINK+="board_1"
```

The ATTRS{serial} should be replaced by your boards unique serial number.
This can be found with udevadm info {/dev/tty{DEV_BOARD}} on Linux.
