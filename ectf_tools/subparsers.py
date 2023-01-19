# 2023 eCTF
# Kyle Scaplen
#
# (c) 2023 The MITRE Corporation
#
# This source file is part of an example system for MITRE's 2023 Embedded
# CTF (eCTF). This code is being provided only for educational purposes for the
# 2023 MITRE eCTF competition, and may not meet MITRE standards for quality.
# Use this code at your own risk!

from pathlib import Path
from typing import Dict, Type

from tap import Tap

subparsers: Dict[str, Type[Tap]] = {}


class eCTFTap(Tap):
    def __init_subclass__(cls, cmd: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if cmd is not None:
            subparsers[cmd] = cls


class BuildParser(eCTFTap):
    design: Path  # path to the design repo (likely in designs/)
    name: str  # tag name of the Docker image
    image: str = "ectf"  # name of the Docker image


class SubparserBuildEnv(BuildParser, cmd="build.env"):
    """Build the environment"""

    docker_dir: Path = Path(
        "docker_env"
    )  # path to the docker env within the design repo
    dockerfile: str = "build_image.Dockerfile"  # name of the dockerfile


class SubparserBuildTools(BuildParser, cmd="build.tools"):
    """Build the tools"""

    tools_in: Path = Path(
        "host_tools"
    )  # path to the host tools directory in the design repo


class SubparserBuildDepl(BuildParser, cmd="build.depl"):
    """Build a deployment"""

    deployment: str  # name of the deployment
    depl_in: Path = Path(
        "deployment"
    )  # path to the deployment directory in the design repo


class BuildDevParser(BuildParser):
    """Build a device"""

    deployment: str  # name of the deployment


class SubparserBuildCarFobPair(BuildDevParser, cmd="build.car_fob_pair"):
    """Build a car and paired fob pair"""

    car_name: str  # name of the car output files
    fob_name: str  # name of the fob output files
    car_out: Path  # directory to mount to output built car to
    fob_out: Path  # directory to mount to output built fob to
    car_id: int  # ID of the car to build
    pair_pin: str  # car pairing PIN
    car_in: Path = Path("car")  # path to the car directory in the design repo
    fob_in: Path = Path("fob")  # path to the fob directory in the design repo
    car_unlock_secret: str = "Car Unlocked"  # unlock secret to put in the car EEPROM
    car_feature1_secret: str = (  # feature 1 secret to put in the car EEPROM
        "Feature 1 Enabled: Heated Seats"
    )
    car_feature2_secret: str = (  # feature 2 secret to put in the car EEPROM
        "Feature 2 Enabled: Extended Range"
    )
    car_feature3_secret: str = (  # feature 3 secret to put in the car EEPROM
        "Feature 3 Enabled: Valet Mode"
    )


class SubparserBuildFob(BuildDevParser, cmd="build.fob"):
    """Build an unpaired fob"""

    fob_name: str  # name of the fob output files
    fob_out: Path  # directory to mount to output built fob to
    fob_in: Path = Path("fob")  # path to the fob directory in the design repo


class DockerRunParser(eCTFTap):
    name: str  # tag name of the Docker image
    image: str = "ectf"  # name of the Docker image


class SubparserUnlockTool(DockerRunParser, cmd="run.unlock"):
    """Run the unlock tool"""

    car_bridge: int


class SubparserPairTool(DockerRunParser, cmd="run.pair"):
    """Run the pair tool"""

    unpaired_fob_bridge: int
    paired_fob_bridge: int
    pair_pin: str


class SubparserEnableTool(DockerRunParser, cmd="run.enable"):
    """Run the enable tool"""

    package_in: Path
    package_name: str
    fob_bridge: int


class SubparserPackageTool(DockerRunParser, cmd="run.package"):
    """Run the package tool"""

    deployment: str  # name of the deployment
    package_out: Path
    package_name: str
    car_id: str
    feature_number: int


class SubparserDevLoadHW(eCTFTap, cmd="device.load_hw"):
    """Load a firmware onto the device"""

    dev_in: Path  # path to the device build directory
    dev_name: str  # name of the device
    dev_serial: str  # specify the serial port


class SubparserDevLoadSecHW(eCTFTap, cmd="device.load_sec_hw"):
    """Load a firmware onto the secure device"""

    dev_in: Path  # path to the device build directory
    dev_name: str  # name of the device
    dev_serial: str  # specify the serial port


class SubparserDevModeChange(eCTFTap, cmd="device.mode_change"):
    """Change the mode of the secure bootloader"""

    dev1_serial: str  # serial port of the first device
    dev2_serial: str  # serial port of the second device


class SubparserDevBridge(eCTFTap, cmd="device.bridge"):
    """Start a serial-to-socket bridge"""

    bridge_id: int  # Bridge ID to set up
    dev_serial: str  # serial port to open
