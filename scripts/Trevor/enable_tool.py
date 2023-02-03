#!/usr/bin/python3 -u

# @file enable_tool
# @author Frederich Stine
# @brief host tool for enabling a feature on a fob
# @date 2023
#
# This source file is part of an example system for MITRE's 2023 Embedded
# CTF (eCTF). This code is being provided only for educational purposes for the
# 2023 MITRE eCTF competition, and may not meet MITRE standards for quality.
# Use this code at your own risk!
#
# @copyright Copyright (c) 2023 The MITRE Corporation

import serial
import argparse


# @brief Function to send commands to enable a feature on a fob
# @param fob_bridge, bridged serial connection to fob
# @param package_name, name of the package file to read from
def enable(fob_bridge, package_name):

    # Connect fob to serial
    fob_connection = serial.Serial(fob_bridge, 115200, timeout=1)
    fob_connection.reset_input_buffer()

    # Send enable command to fob
    fob_connection.write(b"enable\n")

    # Open and read binary data from package file
    with open(f"/package_dir/{package_name}", "rb") as fhandle:
        message = fhandle.read()

    # Send package to fob
    fob_connection.write(message)

    # Set timeout for if enable fails
    fob_connection.timeout = 5

    # Try to receive data - if failed, enabling failed
    try:
        enable_success = fob_connection.read(7)
        while len(enable_success) != 7:
            enable_success += fob_connection.read(7 - len(enable_success))

        print(enable_success)
    except serial.SerialTimeoutException:
        print("Failed to enable feature")

    return 0


# @brief Main function
#
# Main function handles parsing arguments and passing them to program
# function.
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fob-bridge", help="Serial port for the fob", type=str, required=True,
    )
    parser.add_argument(
        "--package-name", help="Name of the package file", type=str, required=True,
    )

    args = parser.parse_args()

    enable(args.fob_bridge, args.package_name)


if __name__ == "__main__":
    main()
