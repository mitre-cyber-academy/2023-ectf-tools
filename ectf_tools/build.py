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

import docker
import docker.errors
from docker.utils import tar
from pathlib import Path

from ectf_tools.utils import run_shell, get_logger, zip_step_returns, HandlerRet
from ectf_tools.device import FW_FLASH_SIZE, FW_EEPROM_SIZE
from ectf_tools.subparsers import (
    SubparserBuildEnv,
    SubparserBuildTools,
    SubparserBuildDepl,
    SubparserBuildCarFobPair,
    SubparserBuildFob,
)


async def env(
    design: Path,
    name: str,
    image: str = SubparserBuildEnv.image,
    docker_dir: Path = SubparserBuildEnv.docker_dir,
    dockerfile: str = SubparserBuildEnv.dockerfile,
    logger: logging.Logger = None,
) -> HandlerRet:
    tag = f"{image}:{name}"
    logger = logger or get_logger()
    logger.info(f"Building image {tag}")

    # Add build directory to context
    build_dir = design.resolve() / docker_dir
    dockerfile_name = build_dir / dockerfile
    with open(dockerfile_name, "r") as df:
        dockerfile = ("Dockerfile", df.read())
    dockerfile = tar(build_dir, dockerfile=dockerfile)

    # run docker build
    client = docker.from_env()
    try:
        _, logs_raw = client.images.build(
            tag=tag, fileobj=dockerfile, custom_context=True,
        )
    except docker.errors.BuildError as e:
        logger.error(f"Docker build error: {e}")
        for log in e.build_log:
            if "stream" in log and log["stream"].strip():
                logger.error(log["stream"].strip())
        raise
    logger.info(f"Built image {tag}")

    logs = "".join([d["stream"] for d in list(logs_raw) if "stream" in d])
    logging.debug(logs)
    return logs.encode(), b""


async def tools(
    design: Path,
    name: str,
    image: str = SubparserBuildTools.image,
    tools_in: Path = SubparserBuildTools.tools_in,
    logger: logging.Logger = None,
) -> HandlerRet:
    tag = f"{image}:{name}"
    logger = logger or get_logger()
    logger.info(f"{tag}: Building tools")
    tool_dir = str(design.resolve() / tools_in)
    output = await run_shell(
        "docker run"
        f' -v "{tool_dir}":/tools_in:ro'
        f" -v {image}.{name}.tools.vol:/tools_out"
        " --workdir=/tools_in"
        f" {tag} make TOOLS_OUT_DIR=/tools_out"
    )
    logger.info(f"{tag}: Built tools")
    return output


async def depl(
    design: Path,
    name: str,
    deployment: str,
    image: str = SubparserBuildDepl.image,
    depl_in: Path = SubparserBuildDepl.depl_in,
    logger: logging.Logger = None,
) -> HandlerRet:
    tag = f"{image}:{name}"
    logger = logger or get_logger()
    logger.info(f"{tag}: Building deployment {deployment}")
    depl_dir = str(design.resolve() / depl_in)
    output = await run_shell(
        "docker run"
        f' -v "{depl_dir}":/depl_in:ro'
        f" -v {image}.{name}.{deployment}.secrets.vol:/secrets"
        " --workdir=/depl_in"
        f" {tag} make SECRETS_DIR=/secrets"
    )
    logger.info(f"{tag}: Built deployment {deployment}")
    return output


async def car_fob_pair(
    design: Path,
    name: str,
    deployment: str,
    car_name: str,
    fob_name: str,
    car_out: Path,
    fob_out: Path,
    car_id: int,
    pair_pin: int,
    car_in: Path = SubparserBuildCarFobPair.car_in,
    fob_in: Path = SubparserBuildCarFobPair.fob_in,
    car_unlock_secret: str = SubparserBuildCarFobPair.car_unlock_secret,
    car_feature1_secret: str = SubparserBuildCarFobPair.car_feature1_secret,
    car_feature2_secret: str = SubparserBuildCarFobPair.car_feature2_secret,
    car_feature3_secret: str = SubparserBuildCarFobPair.car_feature3_secret,
    image: str = SubparserBuildCarFobPair.image,
    logger: logging.Logger = None,
) -> HandlerRet:
    """
    Build car and paired fob pair
    """

    # Image information
    tag = f"{image}:{name}"
    logger = logger or get_logger()
    logger.info(f"{tag}:{deployment}: Building car {car_name}")

    # Car defines
    car_defines = f" CAR_ID={car_id}"

    # Build car
    car_output = await make_dev(
        image=image,
        name=name,
        design=design,
        deployment=deployment,
        dev_name=car_name,
        dev_in=car_in,
        dev_out=car_out,
        defines=car_defines,
        make_target="car",
        logger=logger,
        replace_secrets=True,
        unlock_secret=car_unlock_secret,
        feature1_secret=car_feature1_secret,
        feature2_secret=car_feature2_secret,
        feature3_secret=car_feature3_secret,
    )

    # Fob defines
    fob_defines = f" CAR_ID={car_id}" f" PAIR_PIN={pair_pin}"

    # Build fob
    fob_output = await make_dev(
        image=image,
        name=name,
        design=design,
        deployment=deployment,
        dev_name=fob_name,
        dev_in=fob_in,
        dev_out=fob_out,
        defines=fob_defines,
        make_target="paired_fob",
        logger=logger,
        replace_secrets=False,
    )

    return zip_step_returns([car_output, fob_output])


async def fob(
    design: Path,
    name: str,
    deployment: str,
    fob_name: str,
    fob_out: Path,
    image: str = SubparserBuildFob.image,
    fob_in: Path = SubparserBuildFob.fob_in,
    logger: logging.Logger = None,
) -> HandlerRet:
    """
    Build unpaired fob firmware
    """

    # Image information
    tag = f"{image}:{name}"
    logger = logger or get_logger()
    logger.info(f"{tag}:{deployment}: Building unpaired fob {fob_name}")

    # Unpaired fob defines
    fob_defines = ""

    # Build fob
    output = await make_dev(
        image=image,
        name=name,
        design=design,
        deployment=deployment,
        dev_name=fob_name,
        dev_in=fob_in,
        dev_out=fob_out,
        defines=fob_defines,
        make_target="unpaired_fob",
        logger=logger,
        replace_secrets=False,
    )

    return output


async def make_dev(
    image: str,
    name: str,
    design: str,
    deployment: str,
    dev_name: str,
    dev_in: Path,
    dev_out: Path,
    defines: str,
    make_target: str,
    logger: logging.Logger,
    replace_secrets: bool,
    unlock_secret: str = "Car Unlocked",
    feature1_secret: str = "Feature 1 Enabled: Heated Seats",
    feature2_secret: str = "Feature 2 Enabled: Extended Range",
    feature3_secret: str = "Feature 3 Enabled: Valet Mode",
) -> HandlerRet:
    """
    Build device firmware
    """
    tag = f"{image}:{name}"

    # Setup full container paths
    bin_path = f"/dev_out/{dev_name}.bin"
    elf_path = f"/dev_out/{dev_name}.elf"
    eeprom_path = f"/dev_out/{dev_name}.eeprom"
    dev_in = (design / dev_in).resolve()
    dev_out = dev_out.resolve()

    # Create output directory
    if not dev_out.exists():
        logger.info(f"{tag}:{deployment}: Making output directory {dev_out}")
        dev_out.mkdir()

    # Compile
    output = await run_shell(
        "docker run"
        f' -v "{str(dev_in)}":/dev_in:ro'
        f' -v "{str(dev_out)}":/dev_out'
        f" -v {image}.{name}.{deployment}.secrets.vol:/secrets"
        " --workdir=/root"
        f" {tag} /bin/bash -c"
        ' "'
        " cp -r /dev_in/. /root/ &&"
        f" make {make_target}"
        f" {defines}"
        f" SECRETS_DIR=/secrets"
        f" BIN_PATH={bin_path}"
        f" ELF_PATH={elf_path}"
        f" EEPROM_PATH={eeprom_path}"
        '"'
    )

    logger.info(f"{tag}:{deployment}: Built device {dev_name}")

    # Package image, eeprom, and secret
    logger.info(f"{tag}:{deployment}: Packaging image for device {dev_name}")
    bin_path = dev_out / f"{dev_name}.bin"
    eeprom_path = dev_out / f"{dev_name}.eeprom"
    image_path = dev_out / f"{dev_name}.img"

    package_device(
        bin_path,
        eeprom_path,
        image_path,
        replace_secrets,
        unlock_secret,
        feature1_secret,
        feature2_secret,
        feature3_secret,
    )

    logger.info(f"{tag}:{deployment}: Packaged device {dev_name} image")

    return output


def package_device(
    bin_path: Path,
    eeprom_path: Path,
    image_path: Path,
    replace_secrets: bool,
    unlock_secret: str,
    feature1_secret: str,
    feature2_secret: str,
    feature3_secret: str,
):
    """
    Package a device image for use with the bootstrapper

    Accepts up to 64 bytes (encoded in hex) to insert as a secret in EEPROM
    """
    # Read input bin file
    bin_data = bin_path.read_bytes()

    # Pad bin data to max size
    image_bin_data = bin_data.ljust(FW_FLASH_SIZE, b"\xff")

    # Read EEPROM data
    eeprom_data = eeprom_path.read_bytes()

    # Pad EEPROM to max size
    image_eeprom_data = eeprom_data.ljust(FW_EEPROM_SIZE, b"\xff")

    # Put secrets in EEPROM if used
    if replace_secrets:
        # Convert secrets to bytes
        unlock_secret = unlock_secret.encode()
        feature1_secret = feature1_secret.encode()
        feature2_secret = feature2_secret.encode()
        feature3_secret = feature3_secret.encode()

        # Check secret lengths
        if len(unlock_secret) > 64:
            raise Exception(f"Unlock secret too long ({len(unlock_secret)} > 64)")

        if len(feature1_secret) > 64:
            raise Exception(f"Feature 1 secret too long ({len(feature1_secret)} > 64)")

        if len(feature2_secret) > 64:
            raise Exception(f"Feature 2 secret too long ({len(feature2_secret)} > 64)")

        if len(feature3_secret) > 64:
            raise Exception(f"Feature 3 secret too long ({len(feature3_secret)} > 64)")

        # Pad secrets to 64 bytes
        unlock_secret = unlock_secret.ljust(64, b".")
        feature1_secret = feature1_secret.ljust(64, b".")
        feature2_secret = feature2_secret.ljust(64, b".")
        feature3_secret = feature3_secret.ljust(64, b".")

        # Replace end of EEPROM data with secret values
        image_eeprom_data = (
            image_eeprom_data[: FW_EEPROM_SIZE - 256]
            + feature3_secret
            + feature2_secret
            + feature1_secret
            + unlock_secret
        )

    # Create phys_image.bin
    image_data = image_bin_data + image_eeprom_data

    # Write output binary
    image_path.write_bytes(image_data)
