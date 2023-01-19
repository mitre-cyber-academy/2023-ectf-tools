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
from typing import Tuple, Callable, Awaitable, List


HandlerRet = List[Tuple[bytes, bytes]]
HandlerTy = Callable[..., Awaitable[Tuple[bytes, bytes]]]

SOCKET_BASE = 1337


class CmdFailedError(Exception):
    pass


async def run_shell(cmd: str, logger: logging.Logger = None) -> HandlerRet:
    logger = logger or logging.getLogger("eCTFLogger")
    logger.debug(f"Running command {repr(cmd)}")
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )

    stdout_raw, stderr_raw = await proc.communicate()
    stdout = stdout_raw.decode(errors="backslashreplace")
    stderr = stderr_raw.decode(errors="backslashreplace")
    stdout_msg = f"STDOUT:\n{stdout}" if stdout else "NO STDOUT"
    stderr_msg = f"STDERR:\n{stderr}" if stderr else "NO STDERR"
    if proc.returncode:
        logger.error(stdout_msg)
        logger.error(stderr_msg)
        raise CmdFailedError(
            f"Tool build failed with return code {proc.returncode}", stdout, stderr
        )
    logger.debug(stdout_msg)
    logger.debug(stderr_msg)
    return [(stdout_raw, stderr_raw)]


def get_logger() -> logging.Logger:
    return logging.getLogger("eCTFLogger")


def zip_step_returns(return_list: List[HandlerRet]) -> HandlerRet:

    # A single run_shell returns a 1-length list of stream tuples
    # Add all of those single elements to one list
    zipped_return = return_list[0]
    for ret in return_list[1:]:
        zipped_return.append(ret[0])

    return zipped_return
