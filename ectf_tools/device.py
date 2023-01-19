# 2023 eCTF
# Kyle Scaplen
#
# (c) 2023 The MITRE Corporation
#
# This source file is part of an example system for MITRE's 2023 Embedded
# CTF (eCTF). This code is being provided only for educational purposes for the
# 2023 MITRE eCTF competition, and may not meet MITRE standards for quality.
# Use this code at your own risk!

import asyncio
import logging
import socket
import select
from enum import Enum
from pathlib import Path
from rich.progress import Progress
from typing import Optional

from serial import Serial
from serial.tools import list_ports
from serial.serialutil import SerialException

from ectf_tools.utils import CmdFailedError, get_logger, HandlerRet, SOCKET_BASE


"""
Device Image Sizes
"""

BLOCK_SIZE = 16
PAGE_SIZE = 1024

FLASH_PAGES = 256
FLASH_SIZE = FLASH_PAGES * PAGE_SIZE
EEPROM_PAGES = 2
EEPROM_SIZE = EEPROM_PAGES * PAGE_SIZE

FW_FLASH_PAGES = 110
FW_FLASH_SIZE = FW_FLASH_PAGES * PAGE_SIZE
FW_FLASH_BLOCKS = FW_FLASH_SIZE // BLOCK_SIZE

FW_EEPROM_PAGES = 2
FW_EEPROM_SIZE = FW_EEPROM_PAGES * PAGE_SIZE
FW_EEPROM_BLOCKS = FW_EEPROM_SIZE // BLOCK_SIZE

TOTAL_FW_SIZE = FW_FLASH_SIZE + FW_EEPROM_SIZE
TOTAL_FW_PAGES = FW_FLASH_PAGES + FW_EEPROM_PAGES
TOTAL_FW_BLOCKS = FW_FLASH_BLOCKS + FW_EEPROM_BLOCKS


class BootloaderResponseCode(Enum):
    RequestUpdate = b"\x00"
    StartUpdate = b"\x01"
    UpdateInitFlashEraseOK = b"\x02"
    UpdateInitEEPROMEraseOK = b"\x03"
    UpdateInitEEPROMEraseError = b"\x04"
    AppBlockInstallOK = b"\x05"
    AppBlockInstallError = b"\x06"
    EEPROMBlockInstallOK = b"\x07"
    EEPROMBlockInstallError = b"\x08"
    AppInstallOK = b"\x09"
    AppInstallError = b"\x0a"


secure_bl_success_codes = list(range(0, 18))
secure_bl_error_codes = list(range(18, 26))
SECURE_BL_UPDATE_COMMAND = b"\x00"

secure_bl_mode_change_success_codes = list(range(0, 8))
secure_bl_mode_change_error_codes = list(range(8, 9))
SECURE_BL_MODE_CHANGE_COMMAND = b"\x00"


def get_serial_port():
    orig_ports = set(list_ports.comports())
    while True:
        ports = set(list_ports.comports())
        new_ports = ports - orig_ports

        if len(new_ports) == 1:
            new_port = new_ports.pop()
            return new_port.device

        orig_ports = ports


def verify_resp(ser: Serial, expected: BootloaderResponseCode):
    resp = ser.read(1)
    while resp == b"":
        resp = ser.read(1)

    assert BootloaderResponseCode(resp) == expected


def verify_sec_resp(ser: Serial, print_out: bool = True, logger: logging.Logger = None):
    resp = ser.read(1)
    while (resp == b"") or (
        not ord(resp) in (secure_bl_success_codes + secure_bl_error_codes)
    ):
        resp = ser.read(1)

    logger = logger or get_logger()

    if ord(resp) not in secure_bl_success_codes:
        logger.error(f"Bootloader responded with: {ord(resp)}")
        raise ValueError()
    if print_out:
        logger.info(f"Success. Bootloader responded with code {ord(resp)}")

    return ord(resp)


def verify_mode_change_resp(
    ser: Serial, dev_num: int, print_out: bool = True, logger: logging.Logger = None
):
    resp = ser.read(1)
    while (resp == b"") or (
        not ord(resp)
        in (secure_bl_mode_change_success_codes + secure_bl_mode_change_error_codes)
    ):
        resp = ser.read(1)

    logger = logger or get_logger()

    if ord(resp) not in secure_bl_mode_change_success_codes:
        logger.error(f"Bootloader {dev_num} responded with: {ord(resp)}")
        raise ValueError()
    if print_out:
        logger.info(f"Success. Bootloader {dev_num} responded with code {ord(resp)}")

    return ord(resp)


async def load_hw(
    dev_in: Path, dev_name: str, dev_serial: str, logger: logging.Logger = None,
) -> HandlerRet:
    # Usage: Turn on the device holding SW2, then start this script

    logger = logger or get_logger()

    # Set up file references
    image_path = dev_in / f"{dev_name}.img"

    # Try to connect to the serial port
    logger.info(f"Connecting to serial port {dev_serial}...")
    ser = Serial(dev_serial, 115200, timeout=2)
    ser.reset_input_buffer()
    logger.info(f"Connection opened on {dev_serial}")

    # Open firmware
    logger.info("Reading image file...")
    if not image_path.exists():
        ser.close()
        raise CmdFailedError(f"Image file {image_path} not found")

    fw_data = image_path.read_bytes()
    fw_size = len(fw_data)
    if fw_size != TOTAL_FW_SIZE:
        ser.close()
        raise CmdFailedError(
            f"Invalid image size 0x{fw_size:X}. Expected 0x{TOTAL_FW_SIZE:X}"
        )

    # Wait for bootloader ready
    logger.info("Requesting update...")
    ser.write(BootloaderResponseCode.RequestUpdate.value)
    try:
        verify_resp(ser, BootloaderResponseCode.StartUpdate)
    except AssertionError:
        ser.close()
        raise CmdFailedError("Bootloader did not start an update")

    # Wait for Flash erase
    logger.info("Waiting for Flash Erase...")
    try:
        verify_resp(ser, BootloaderResponseCode.UpdateInitFlashEraseOK)
    except AssertionError:
        ser.close()
        raise CmdFailedError("Error while erasing Flash")

    # Wait for EEPROM erase
    logger.info("Waiting for EEPROM Erase...")
    try:
        verify_resp(ser, BootloaderResponseCode.UpdateInitEEPROMEraseOK)
    except AssertionError:
        ser.close()
        raise CmdFailedError("Error while erasing EEPROM")

    # Send data in 16-byte blocks
    logger.info("Sending firmware...")
    total_bytes = len(fw_data)
    block_count = 0
    i = 0
    with Progress() as progress:
        task = progress.add_task("Sending firmware...", total=total_bytes)
        while i < total_bytes:
            block_bytes = fw_data[i : i + BLOCK_SIZE]  # noqa
            ser.write(block_bytes)

            try:
                if block_count < FW_FLASH_BLOCKS:
                    verify_resp(ser, BootloaderResponseCode.AppBlockInstallOK)
                else:
                    verify_resp(ser, BootloaderResponseCode.EEPROMBlockInstallOK)
            except AssertionError:
                ser.close()
                raise CmdFailedError(f"Install failed at block {block_count+1}")

            i += BLOCK_SIZE
            block_count += 1
            progress.update(task, advance=len(block_bytes))

    try:
        verify_resp(ser, BootloaderResponseCode.AppInstallOK)
    except AssertionError:
        ser.close()
        raise CmdFailedError("Image Failed to Install")

    logger.info("Image Installed")
    return b"", b""


async def load_sec_hw(
    dev_in: Path, dev_name: str, dev_serial: str, logger: logging.Logger = None,
) -> HandlerRet:
    # Usage: Turn on the device holding SW2, then start this script

    logger = logger or get_logger()

    # Set up file references
    image_path = dev_in / f"{dev_name}.img"

    # Try to connect to the serial port
    logger.info(f"Connecting to serial port {dev_serial}...")
    ser = Serial(dev_serial, 115200, timeout=2)
    ser.reset_input_buffer()
    logger.info(f"Connection opened on {dev_serial}")

    # Open firmware
    logger.info("Reading image file...")
    if not image_path.exists():
        ser.close()
        raise CmdFailedError(f"Image file {image_path} not found")

    fw_data = image_path.read_bytes()

    # Wait for bootloader ready
    logger.info("Requesting update...")
    ser.write(SECURE_BL_UPDATE_COMMAND)

    resp = -1
    while resp != secure_bl_success_codes[2]:
        try:
            resp = verify_sec_resp(ser, logger=logger)
        except ValueError:
            ser.close()
            raise CmdFailedError("Load HW Failed")

    # Send data in 16-byte blocks
    logger.info("Update started")
    total_bytes = len(fw_data)
    block_count = 0
    i = 0

    with Progress() as progress:
        task = progress.add_task("Sending firmware...", total=total_bytes)
        while i < total_bytes:
            block_bytes = fw_data[i : i + BLOCK_SIZE]
            ser.write(block_bytes)
            try:
                verify_sec_resp(ser, print_out=False, logger=logger)
            except ValueError:
                ser.close()
                raise CmdFailedError(f"Install failed at block {block_count+1}")

            i += BLOCK_SIZE
            block_count += 1
            progress.update(task, advance=len(block_bytes))

    logger.info("Listening for update status...")
    resp = -1
    while resp != secure_bl_success_codes[-1]:
        try:
            resp = verify_sec_resp(ser, logger=logger)
        except AssertionError:
            ser.close()
            raise CmdFailedError("Image Failed to Install")

    logger.info("Image Installed")
    return b"", b""


async def mode_change(
    dev1_serial: str, dev2_serial: str, logger: logging.Logger = None
):
    logger = logger or logging.getLogger()

    # Open serial ports
    ser1 = Serial(dev1_serial, 115200, timeout=2)
    ser1.reset_input_buffer()

    ser2 = Serial(dev2_serial, 115200, timeout=2)
    ser2.reset_input_buffer()

    logger.info(f"Connected to bootloaders on {dev1_serial} and {dev2_serial}")

    # Wait for bootloader ready
    logger.info("Requesting mode change")
    ser1.write(SECURE_BL_MODE_CHANGE_COMMAND)
    ser2.write(SECURE_BL_MODE_CHANGE_COMMAND)
    verify_mode_change_resp(ser1, 1, logger=logger)
    verify_mode_change_resp(ser2, 2, logger=logger)

    # Receive data
    d1 = ser1.read(32)
    verify_mode_change_resp(ser1, 1, logger=logger)
    d2 = ser2.read(32)
    verify_mode_change_resp(ser2, 2, logger=logger)

    # Forward data
    ser1.write(d2)
    verify_mode_change_resp(ser1, 1, logger=logger)
    ser2.write(d1)
    verify_mode_change_resp(ser2, 2, logger=logger)

    # Receive data
    d1 = ser1.read(32)
    verify_mode_change_resp(ser1, 1, logger=logger)
    d2 = ser2.read(32)
    verify_mode_change_resp(ser2, 2, logger=logger)

    # Forward data
    ser1.write(d2)
    verify_mode_change_resp(ser1, 1, logger=logger)
    ser2.write(d1)
    verify_mode_change_resp(ser2, 2, logger=logger)

    # Try receiving d2 first
    d2 = ser2.read(32)
    if len(d2) == 32:
        # Continue, forward d2 to d1
        verify_mode_change_resp(ser2, 2, logger=logger)
        ser1.write(d2)
        verify_mode_change_resp(ser1, 1, logger=logger)

        # Receive from d1
        d1 = ser1.read(32)
        verify_mode_change_resp(ser1, 1, logger=logger)
        ser2.write(d1)
        verify_mode_change_resp(ser2, 2, logger=logger)
    else:
        # Need to receive d1 first
        d1 = ser1.read(32)
        verify_mode_change_resp(ser1, 1, logger=logger)
        ser2.write(d1)
        verify_mode_change_resp(ser2, 2, logger=logger)

        # Receive from d2
        d2 = ser2.read(32)
        verify_mode_change_resp(ser2, 2, logger=logger)
        ser1.write(d2)
        verify_mode_change_resp(ser1, 1, logger=logger)

    logger.info("Mode Change Complete")
    return b"", b""


class Port:
    def __init__(self, device_serial: str, baudrate=115200, log_level=logging.INFO):
        self.device_serial = device_serial
        self.baudrate = baudrate
        self.ser = None

        # Set up logger
        self.logger = logging.getLogger(f"{device_serial}_log")
        self.logger.info(f"Ready to connect to device on serial {self.device_serial}")

    def active(self) -> bool:
        # If not connected, try to connect to serial device
        if not self.ser:
            try:
                ser = Serial(self.device_serial, baudrate=self.baudrate, timeout=0.1)
                ser.reset_input_buffer()
                self.ser = ser
                self.logger.info(f"Connection opened on {self.device_serial}")
            except (SerialException, OSError):
                pass
        return bool(self.ser)

    def read_msg(self) -> Optional[bytes]:
        if not self.active():
            return None

        try:
            msg = self.ser.read()
            if msg != b"":
                return msg
            return None
        except (SerialException, OSError):
            self.close()
            return None

    def send_msg(self, msg: bytes) -> bool:
        if not self.active():
            return False

        try:
            self.ser.write(msg)
            return True
        except (SerialException, OSError):
            self.close()
            return False

    def close(self):
        self.logger.warning(f"Connection closed on {self.device_serial}")
        self.ser = None


class Sock:
    def __init__(self, bridge_id: int, q_len=1, log_level=logging.INFO):
        self.bridge_id = bridge_id

        # Set up socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", int(bridge_id)))
        self.sock.listen(q_len)
        self.csock = None

        # Set up logger
        self.logger = logging.getLogger(f"{bridge_id}_log")
        self.logger.info(f"Ready to connect to socket on port {self.bridge_id}")

    @staticmethod
    def sock_ready(sock: socket.SocketType) -> bool:
        ready, _, _ = select.select([sock], [], [], 0)
        return bool(ready)

    def active(self) -> bool:
        # Try to accept new client
        if not self.csock:
            if self.sock_ready(self.sock):
                self.logger.info(f"Connection opened on {self.bridge_id}")
                self.csock, _ = self.sock.accept()
        return bool(self.csock)

    def read_msg(self) -> Optional[bytes]:
        if not self.active():
            return None

        try:
            if self.sock_ready(self.csock):
                data = self.csock.recv(4096)

                # Connection closed
                if not data:
                    self.close()
                    return None

                return data
            return None
        except (ConnectionResetError, BrokenPipeError):
            # Cleanly handle forced closed connection
            self.close()
            return None

    def send_msg(self, msg: bytes) -> bool:
        if not self.active():
            return False

        try:
            self.csock.sendall(msg)
            return True
        except (ConnectionResetError, BrokenPipeError):
            # Cleanly handle forced closed connection
            self.close()
            return False

    def close(self):
        self.logger.warning(f"Conection closed on {self.bridge_id}")
        self.csock = None


def poll_bridge(host_sock: Sock, serial_port: Port):
    if host_sock.active():
        msg = host_sock.read_msg()

        # Send message to device
        if serial_port.active():
            if msg is not None:
                serial_port.send_msg(msg)

    if serial_port.active():
        msg = serial_port.read_msg()

        # Send message to host
        if host_sock.active():
            if msg is not None:
                host_sock.send_msg(msg)


async def bridge(
    bridge_id: int, dev_serial: str, logger: logging.Logger = None
) -> HandlerRet:

    logger = logger or get_logger()
    logger.info(
        f"Starting bridge between host socket {bridge_id} and serial {dev_serial}"
    )

    # Open interfaces
    bridge_id += SOCKET_BASE
    host_sock = Sock(bridge_id)
    serial_port = Port(dev_serial)

    try:
        while True:
            poll_bridge(host_sock, serial_port)
            await asyncio.sleep(0)
    except KeyboardInterrupt:
        logger.info("Shutting down bridge")
        host_sock.close()
        serial_port.close()

    logger.info("Bridge shut-down")
    return b"", b""
