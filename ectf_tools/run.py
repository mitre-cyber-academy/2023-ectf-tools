# 2023 eCTF
# Kyle Scaplen
#
# (c) 2023 The MITRE Corporation
#
# This source file is part of an example system for MITRE's 2023 Embedded
# CTF (eCTF). This code is being provided only for educational purposes for the
# 2023 MITRE eCTF competition, and may not meet MITRE standards for quality.
# Use this code at your own risk!

import logging
from pathlib import Path

from ectf_tools.utils import run_shell, get_logger, SOCKET_BASE
from ectf_tools.subparsers import (
    SubparserUnlockTool,
    SubparserPairTool,
    SubparserEnableTool,
    SubparserPackageTool,
)


async def unlock(
    name: str,
    car_bridge: int,
    image: str = SubparserUnlockTool.image,
    logger: logging.Logger = None,
):
    tag = f"{image}:{name}"
    logger = logger or get_logger()
    logger.info(f"{tag} Running unlock tool")

    car_bridge += SOCKET_BASE

    ret = await run_shell(
        "docker run"
        " --rm"
        " --add-host ectf-net:host-gateway"
        f" -v {image}.{name}.tools.vol:/tools_out:ro"
        " --workdir=/tools_out"
        f" {tag} ./unlock_tool --car-bridge {car_bridge}",
        logger,
    )

    stdout, stderr = ret[0]
    print(stdout.decode(errors="backslashreplace"))

    logger.info(f"{tag}: Unlock tool run")
    return stdout, stderr


async def pair(
    name: str,
    unpaired_fob_bridge: int,
    paired_fob_bridge: int,
    pair_pin: str,
    image: str = SubparserPairTool.image,
    logger: logging.Logger = None,
):
    tag = f"{image}:{name}"
    logger = logger or get_logger()
    logger.info(f"{tag} Running pair tool")

    unpaired_fob_bridge += SOCKET_BASE
    paired_fob_bridge += SOCKET_BASE

    ret = await run_shell(
        "docker run"
        " --rm"
        " --add-host ectf-net:host-gateway"
        f" -v {image}.{name}.tools.vol:/tools_out:ro"
        " --workdir=/tools_out"
        f" {tag} ./pair_tool --unpaired-fob-bridge {unpaired_fob_bridge} "
        f"--paired-fob-bridge {paired_fob_bridge} --pair-pin {pair_pin} ",
        logger,
    )

    stdout, stderr = ret[0]

    logger.info(f"{tag}: Pair tool run")
    return stdout, stderr


async def package(
    name: str,
    deployment: str,
    car_id: str,
    feature_number: int,
    package_out: Path,
    package_name: str,
    image: str = SubparserPackageTool.image,
    logger: logging.Logger = None,
):
    tag = f"{image}:{name}"
    logger = logger or get_logger()
    logger.info(f"{tag} Running package tool")

    package_out = package_out.resolve()

    ret = await run_shell(
        "docker run"
        " --rm"
        " --add-host ectf-net:host-gateway"
        f" -v {image}.{name}.{deployment}.secrets.vol:/secrets"
        f" -v {image}.{name}.tools.vol:/tools_out:ro"
        " --workdir=/tools_out"
        f" -v {str(package_out)}:/package_dir"
        f" {tag} ./package_tool --package-name {package_name}"
        f" --car-id {car_id} --feature-number {feature_number}",
        logger,
    )

    stdout, stderr = ret[0]

    logger.info(f"{tag}: Package tool run")
    return stdout, stderr


async def enable(
    name: str,
    fob_bridge: int,
    package_in: Path,
    package_name: str,
    image: str = SubparserEnableTool.image,
    logger: logging.Logger = None,
):
    tag = f"{image}:{name}"
    logger = logger or get_logger()
    logger.info(f"{tag} Running enable tool")

    package_in = package_in.resolve()

    fob_bridge += SOCKET_BASE

    ret = await run_shell(
        "docker run"
        " --rm"
        " --add-host ectf-net:host-gateway"
        f" -v {image}.{name}.tools.vol:/tools_out:ro"
        " --workdir=/tools_out"
        f" -v {str(package_in)}:/package_dir"
        f" {tag} ./enable_tool --fob-bridge {fob_bridge}"
        f" --package-name {package_name}",
        logger,
    )

    stdout, stderr = ret[0]

    logger.info(f"{tag}: Enable tool run")
    return stdout, stderr
